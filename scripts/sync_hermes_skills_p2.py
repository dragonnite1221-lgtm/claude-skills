# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from sync_hermes_skills_base import *  # noqa: F403,E402
# fmt: off
from sync_hermes_skills_p1 import HERMES_SKILLS_DIR, REPO_ROOT, TARGET_SUBDIR, discover_skills, sync_skill, write_index  # noqa: E402,E501
# fmt: on


def main():
    p = argparse.ArgumentParser(
        description="Sync claude-code-skills into Hermes Agent (~/.hermes/skills/).",
        epilog="Both tools use the agentskills.io SKILL.md standard. No format conversion needed.",
    )
    p.add_argument(
        "--domain",
        default=None,
        help="Sync only one domain (e.g. engineering, marketing-skill)",
    )
    p.add_argument("--verbose", action="store_true", help="Show each skill")
    p.add_argument("--dry-run", action="store_true", help="Preview only, don't create files")
    p.add_argument("--copy", action="store_true", help="Copy files instead of symlink")
    p.add_argument("--json", action="store_true", help="JSON output")
    p.add_argument(
        "--target",
        default=str(HERMES_SKILLS_DIR),
        help=f"Override Hermes skills dir (default: {HERMES_SKILLS_DIR})",
    )
    args = p.parse_args()

    target_root = Path(args.target).expanduser() / TARGET_SUBDIR
    domains = [args.domain] if args.domain else None
    skills = discover_skills(REPO_ROOT, domains)

    if not skills:
        msg = f"No skills found in {REPO_ROOT}"
        if args.json:
            print(json.dumps({"status": "error", "message": msg}))
        else:
            print(f"[error] {msg}", file=sys.stderr)
        sys.exit(1)

    if not args.dry_run:
        target_root.mkdir(parents=True, exist_ok=True)

    counts = {"new": 0, "skip": 0, "would": 0}
    for s in skills:
        result = sync_skill(s, target_root, args.copy, args.verbose, args.dry_run)
        counts[result] += 1

    # Write index
    if not args.dry_run:
        idx_path = write_index(target_root, skills)
    else:
        idx_path = target_root / "skills-index.json"

    summary = {
        "status": "ok",
        "target": str(target_root),
        "total_skills": len(skills),
        "new": counts["new"],
        "skipped": counts["skip"],
        "dry_run": args.dry_run,
        "mode": "copy" if args.copy else "symlink",
        "index": str(idx_path),
        "domains": list({s["domain"] for s in skills}),
    }

    if args.json:
        print(json.dumps(summary, indent=2))
        return

    action = "Would sync" if args.dry_run else "Synced"
    print(f"{action} {len(skills)} skills to {target_root}")
    print(f"  New: {counts['new']}  Skipped: {counts['skip']}")
    print(f"  Mode: {'copy' if args.copy else 'symlink'}")
    if not args.dry_run:
        print(f"  Index: {idx_path}")
    print()
    print("Hermes will discover these skills via /skills or /<skill-name>.")
    print("No format conversion needed — both tools use agentskills.io SKILL.md standard.")
