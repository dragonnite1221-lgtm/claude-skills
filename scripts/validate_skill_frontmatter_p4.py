# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from validate_skill_frontmatter_base import *  # noqa: F403,E402
# fmt: off
from validate_skill_frontmatter_p3 import validate_repo  # noqa: E402,E501
# fmt: on


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
