# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from validate_skill_frontmatter_base import *  # noqa: F403,E402
# fmt: off
from validate_skill_frontmatter_p1 import DEFAULT_FRONTMATTER_ALLOWLIST, ValidationIssue, load_gemini_sync_module, normalize_repo_path  # noqa: E402,E501
from validate_skill_frontmatter_p2 import validate_skill_frontmatter  # noqa: E402,E501
# fmt: on


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
