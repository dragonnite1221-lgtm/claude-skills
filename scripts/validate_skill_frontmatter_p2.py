# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from validate_skill_frontmatter_base import *  # noqa: F403,E402
# fmt: off
from validate_skill_frontmatter_p1 import ValidationIssue, is_under_repo, normalize_repo_path, parse_frontmatter_fields, source_path_for_skill  # noqa: E402,E501
# fmt: on


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
