# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from decision_tracker_base import *  # noqa: F403,E402
# fmt: off
from decision_tracker_p1 import Decision  # noqa: E402,E501
from decision_tracker_p2 import fmt_date, parse_decisions, print_section  # noqa: E402,E501
from decision_tracker_p3 import report_by_owner, report_due_within, report_overdue, report_search, report_summary  # noqa: E402,E501
from decision_tracker_p4 import SAMPLE_DECISIONS_MD, report_conflicts  # noqa: E402,E501
# fmt: on


def load_decisions(decisions_path: Path, demo: bool) -> list[Decision]:
    if demo:
        content = SAMPLE_DECISIONS_MD
    elif decisions_path.exists():
        content = decisions_path.read_text(encoding="utf-8")
    else:
        print(f"  ⚠️  decisions.md not found at: {decisions_path}")
        print(f"  Run with --demo to see sample output.")
        print(f"  To initialize: mkdir -p memory/board-meetings && touch memory/board-meetings/decisions.md")
        sys.exit(1)
    return parse_decisions(content)
def main():
    parser = argparse.ArgumentParser(
        description="Board Meeting Decision Tracker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--file", default="memory/board-meetings/decisions.md",
                        help="Path to decisions.md (default: memory/board-meetings/decisions.md)")
    parser.add_argument("--demo", action="store_true",
                        help="Run with built-in sample data (no file needed)")
    parser.add_argument("--summary", action="store_true",
                        help="Show overview: counts, overdue, recent decisions")
    parser.add_argument("--overdue", action="store_true",
                        help="List all overdue action items")
    parser.add_argument("--due-within", type=int, metavar="DAYS",
                        help="List items due within N days")
    parser.add_argument("--owner", metavar="ROLE",
                        help="Filter action items by owner")
    parser.add_argument("--search", metavar="QUERY",
                        help="Search decisions and rejected proposals")
    parser.add_argument("--conflicts", action="store_true",
                        help="Check for contradictory decisions or DO_NOT_RESURFACE violations")
    parser.add_argument("--all", action="store_true",
                        help="Show all decisions (summary format)")

    args = parser.parse_args()

    if not any([args.summary, args.overdue, args.due_within, args.owner,
                args.search, args.conflicts, getattr(args, "all")]):
        args.summary = True  # Default action

    decisions_path = Path(args.file)
    decisions = load_decisions(decisions_path, args.demo)

    if not decisions:
        print("  No decisions found in decisions.md.")
        sys.exit(0)

    if args.demo:
        print(f"\n  🎯 DEMO MODE — using built-in sample data ({len(decisions)} decisions)")

    if args.summary:
        report_summary(decisions)

    if args.overdue:
        report_overdue(decisions)

    if args.due_within:
        report_due_within(decisions, args.due_within)

    if args.owner:
        report_by_owner(decisions, args.owner)

    if args.search:
        report_search(decisions, args.search)

    if args.conflicts:
        report_conflicts(decisions)

    if getattr(args, "all"):
        print_section(f"ALL DECISIONS ({len(decisions)} total)")
        for d in sorted(decisions, key=lambda x: x.date or date.min, reverse=True):
            status = "📦 SUPERSEDED" if not d.is_active() else ""
            override = "  [OVERRIDE]" if d.has_override() else ""
            print(f"\n  [{fmt_date(d.date)}] {d.title} {status}{override}")
            print(f"    Decision: {d.decision}")
            print(f"    Owner: {d.owner or '—'}  |  Deadline: {fmt_date(d.deadline)}")
            open_actions = [a for a in d.action_items if not a.completed]
            if open_actions:
                print(f"    Open actions: {len(open_actions)}")

    print()
