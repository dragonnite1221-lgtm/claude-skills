#!/usr/bin/env python3
"""Validate SKILL.md frontmatter and Gemini mirror consistency."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


FRONTMATTER_RE = re.compile(r"^---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)

# Intentional test fixture used by engineering/skill-tester. It is kept in the
# Gemini mirror to exercise tooling against a minimal malformed sample.
DEFAULT_FRONTMATTER_ALLOWLIST = {
    "engineering/skill-tester/assets/sample-skill/SKILL.md",
}


@dataclass
class ValidationIssue:
    code: str
    path: str
    message: str


def load_gemini_sync_module(repo_root: Path):
    script_path = repo_root / "scripts" / "sync-gemini-skills.py"
    spec = importlib.util.spec_from_file_location("sync_gemini_skills", script_path)
    if not spec or not spec.loader:
        raise RuntimeError(f"Could not load {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def normalize_repo_path(path: Path, repo_root: Path) -> str:
    try:
        return path.relative_to(repo_root).as_posix()
    except ValueError:
        return str(path)


def is_under_repo(path: Path, repo_root: Path) -> bool:
    try:
        path.relative_to(repo_root)
    except ValueError:
        return False
    return True


def source_path_for_skill(repo_root: Path, skill: dict[str, Any]) -> Path:
    mirror_dir = repo_root / ".gemini" / "skills" / skill["name"]
    return (mirror_dir / skill["source"]).resolve(strict=False)


def parse_frontmatter_fields(skill_md: Path) -> dict[str, str]:
    content = skill_md.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(content)
    if not match:
        return {}

    fields: dict[str, str] = {}
    lines = match.group(1).splitlines()
    index = 0
    while index < len(lines):
        raw_line = lines[index]
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            index += 1
            continue

        if raw_line.startswith((" ", "\t")):
            index += 1
            continue

        key, separator, value = raw_line.partition(":")
        if separator != ":":
            index += 1
            continue

        field_name = key.strip()
        parsed_value = value.strip()
        if parsed_value in {">", ">-", ">+", "|", "|-", "|+"}:
            block_lines: list[str] = []
            index += 1
            while index < len(lines):
                next_line = lines[index]
                if (
                    next_line
                    and not next_line.startswith((" ", "\t"))
                    and ":" in next_line
                ):
                    break
                stripped = next_line.strip()
                if stripped and not stripped.startswith("#"):
                    block_lines.append(stripped)
                index += 1
            fields[field_name] = "\n".join(block_lines).strip()
            continue

        if (
            (parsed_value.startswith('"') and parsed_value.endswith('"'))
            or (parsed_value.startswith("'") and parsed_value.endswith("'"))
        ):
            parsed_value = parsed_value[1:-1].strip()
        fields[field_name] = parsed_value
        index += 1

    return fields


def validate_skill_frontmatter(
    repo_root: Path,
    skills: list[dict[str, Any]],
    allowlist: set[str],
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    for skill in skills:
        source_path = source_path_for_skill(repo_root, skill)
        rel_path = normalize_repo_path(source_path, repo_root)

        if not is_under_repo(source_path, repo_root):
            issues.append(
                ValidationIssue(
                    "external_source",
                    rel_path,
                    f"source SKILL.md for mirror entry {skill['name']} points outside the repository",
                )
            )
            continue

        if rel_path in allowlist:
            continue

        if not source_path.exists():
            issues.append(
                ValidationIssue(
                    "missing_source",
                    rel_path,
                    f"source SKILL.md for mirror entry {skill['name']} does not exist",
                )
            )
            continue

        fields = parse_frontmatter_fields(source_path)
        if not fields:
            issues.append(
                ValidationIssue(
                    "missing_frontmatter",
                    rel_path,
                    "SKILL.md must start with YAML frontmatter delimited by ---",
                )
            )
            continue

        for required_key in ("name", "description"):
            if required_key not in fields:
                issues.append(
                    ValidationIssue(
                        "missing_frontmatter_key",
                        rel_path,
                        f"frontmatter missing required key: {required_key}",
                    )
                )
            elif not fields[required_key].strip():
                issues.append(
                    ValidationIssue(
                        "empty_frontmatter_key",
                        rel_path,
                        f"frontmatter key is empty: {required_key}",
                    )
                )

    return issues


def validate_gemini_mirror(
    repo_root: Path,
    skills: list[dict[str, Any]],
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    gemini_skills_dir = repo_root / ".gemini" / "skills"
    expected_by_name = {skill["name"]: skill for skill in skills}

    if not gemini_skills_dir.exists():
        return [
            ValidationIssue(
                "missing_gemini_skills_dir",
                ".gemini/skills",
                "Gemini skills mirror directory is missing",
            )
        ]

    actual_by_name: dict[str, Path] = {}
    for skill_md in gemini_skills_dir.glob("*/SKILL.md"):
        actual_by_name[skill_md.parent.name] = skill_md

    for stale_name in sorted(set(actual_by_name) - set(expected_by_name)):
        issues.append(
            ValidationIssue(
                "stale_mirror_skill",
                normalize_repo_path(actual_by_name[stale_name], repo_root),
                "Gemini mirror contains a skill not produced by sync-gemini-skills.py",
            )
        )

    for missing_name in sorted(set(expected_by_name) - set(actual_by_name)):
        issues.append(
            ValidationIssue(
                "missing_mirror_skill",
                f".gemini/skills/{missing_name}/SKILL.md",
                "Gemini mirror is missing expected skill symlink",
            )
        )

    for name, skill in sorted(expected_by_name.items()):
        symlink_path = actual_by_name.get(name)
        if symlink_path is None:
            continue
        if not symlink_path.is_symlink():
            issues.append(
                ValidationIssue(
                    "mirror_not_symlink",
                    normalize_repo_path(symlink_path, repo_root),
                    "Gemini mirror SKILL.md must be a symlink to the source SKILL.md",
                )
            )
            continue
        current_target = os.readlink(symlink_path)
        if current_target != skill["source"]:
            issues.append(
                ValidationIssue(
                    "mirror_target_drift",
                    normalize_repo_path(symlink_path, repo_root),
                    f"symlink target drifted: expected {skill['source']!r}, got {current_target!r}",
                )
            )

    index_path = repo_root / ".gemini" / "skills-index.json"
    if not index_path.exists():
        issues.append(
            ValidationIssue(
                "missing_skills_index",
                ".gemini/skills-index.json",
                "Gemini skills index is missing",
            )
        )
        return issues

    try:
        index = json.loads(index_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        issues.append(
            ValidationIssue(
                "invalid_skills_index_json",
                ".gemini/skills-index.json",
                f"Gemini skills index is not valid JSON: {exc}",
            )
        )
        return issues

    expected_index_skills = [
        {
            "name": skill["name"],
            "category": skill["category"],
            "description": skill["description"],
        }
        for skill in skills
    ]
    expected_index_skills.sort(key=lambda item: (item["category"], item["name"]))
    actual_index_skills = index.get("skills")
    if actual_index_skills != expected_index_skills:
        issues.append(
            ValidationIssue(
                "skills_index_drift",
                ".gemini/skills-index.json",
                "skills-index.json does not match sync-gemini-skills.py output",
            )
        )

    if index.get("total_skills") != len(skills):
        issues.append(
            ValidationIssue(
                "skills_index_count_drift",
                ".gemini/skills-index.json",
                f"total_skills should be {len(skills)}, got {index.get('total_skills')!r}",
            )
        )

    return issues


def validate_repo(
    repo_root: Path,
    allowlist: set[str] | None = None,
) -> list[ValidationIssue]:
    repo_root = repo_root.resolve()
    allowlist = set(DEFAULT_FRONTMATTER_ALLOWLIST if allowlist is None else allowlist)
    sync_module = load_gemini_sync_module(repo_root)
    skills = sync_module.find_skills(repo_root)
    issues = validate_skill_frontmatter(repo_root, skills, allowlist)
    issues.extend(validate_gemini_mirror(repo_root, skills))
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate SKILL.md frontmatter and Gemini mirror consistency"
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="Repository root to inspect",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable issue JSON",
    )
    args = parser.parse_args()

    issues = validate_repo(args.repo_root)
    if args.json:
      print(json.dumps([asdict(issue) for issue in issues], indent=2, sort_keys=True))
    elif issues:
        print(f"Skill frontmatter/mirror validation failed: {len(issues)} issue(s)")
        for issue in issues:
            print(f"- [{issue.code}] {issue.path}: {issue.message}")
    else:
        print("Skill frontmatter/mirror validation passed")

    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
