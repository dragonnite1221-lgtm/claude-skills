# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from sync_codex_skills_base import *  # noqa: F403,E402
# fmt: off
from sync_codex_skills_p1 import find_skills  # noqa: E402,E501
from sync_codex_skills_p2 import create_symlinks, generate_skills_index, validate_symlinks  # noqa: E402,E501
# fmt: on


def main():
    parser = argparse.ArgumentParser(
        description="Sync Codex skills symlinks and generate index"
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Show what would be done without making changes"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed output"
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate symlinks after sync"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )

    args = parser.parse_args()

    # Find repository root (where this script lives in scripts/)
    script_path = Path(__file__).resolve()
    repo_root = script_path.parent.parent

    if args.verbose and not args.json:
        print(f"Repository root: {repo_root}")
        print(f"Scanning for skills...")

    # Find all skills
    skills = find_skills(repo_root)

    if not skills:
        if args.json:
            print(json.dumps({"error": "No skills found"}, indent=2))
        else:
            print("No skills found in repository")
        sys.exit(1)

    if args.verbose and not args.json:
        print(f"Found {len(skills)} skills across {len(set(s['category'] for s in skills))} categories")
        print()

    # Create symlinks
    if not args.json:
        mode = "[DRY RUN] " if args.dry_run else ""
        print(f"{mode}Creating symlinks in .codex/skills/...")

    symlink_results = create_symlinks(repo_root, skills, args.dry_run, args.verbose)

    # Generate index
    if not args.json:
        print(f"{mode}Generating .codex/skills-index.json...")

    index = generate_skills_index(repo_root, skills, args.dry_run)

    # Validate if requested
    validation_errors = []
    if args.validate and not args.dry_run:
        if not args.json:
            print("Validating symlinks...")
        validation_errors = validate_symlinks(repo_root, skills)

    # Output results
    if args.json:
        output = {
            "dry_run": args.dry_run,
            "total_skills": len(skills),
            "symlinks": symlink_results,
            "index_generated": not args.dry_run,
            "validation_errors": validation_errors if args.validate else None
        }
        print(json.dumps(output, indent=2))
    else:
        print()
        print("=" * 50)
        print("SUMMARY")
        print("=" * 50)
        print(f"Total skills: {len(skills)}")
        print(f"Symlinks created: {len(symlink_results['created'])}")
        print(f"Symlinks updated: {len(symlink_results['updated'])}")
        print(f"Symlinks unchanged: {len(symlink_results['unchanged'])}")

        if symlink_results['errors']:
            print(f"Errors: {len(symlink_results['errors'])}")
            for err in symlink_results['errors']:
                print(f"  - {err}")

        if validation_errors:
            print(f"Validation errors: {len(validation_errors)}")
            for err in validation_errors:
                print(f"  - {err}")

        print()
        print("Categories:")
        for cat, info in index["categories"].items():
            print(f"  {cat}: {info['count']} skills")

        if args.dry_run:
            print()
            print("No changes made (dry run mode)")
        else:
            print()
            print(f"Index written to: .codex/skills-index.json")
            print(f"Symlinks created in: .codex/skills/")

    # Exit with error if there were issues
    if symlink_results['errors'] or validation_errors:
        sys.exit(1)

    sys.exit(0)
