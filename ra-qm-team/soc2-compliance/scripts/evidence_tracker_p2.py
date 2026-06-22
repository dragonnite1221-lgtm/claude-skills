# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from evidence_tracker_base import *  # noqa: F403,E402
# fmt: off
from evidence_tracker_p1 import EVIDENCE_STATUSES, generate_status_report, load_matrix  # noqa: E402,E501
# fmt: on


def format_status_text(report: Dict[str, Any]) -> str:
    """Format the status report as human-readable text."""
    lines = ["=" * 60, "SOC 2 Evidence Collection Status Report", "=" * 60, ""]

    summary = report["summary"]
    lines.append(f"Report Date: {summary['report_date']}")
    lines.append(f"Total Controls: {summary['total_controls']}")
    lines.append(
        f"Readiness Score: {summary['readiness_score']}% ({summary['readiness_rating']})"
    )
    lines.append("")

    # Status breakdown
    lines.append("--- Status Breakdown ---")
    for status, count in summary["status_breakdown"].items():
        label = EVIDENCE_STATUSES.get(status, status)
        lines.append(f"  {status:15s}: {count:3d}  ({label})")
    lines.append("")

    # By category
    lines.append("--- By Category ---")
    for cat, statuses in report["by_category"].items():
        cat_total = sum(statuses.values())
        cat_collected = statuses.get("collected", 0)
        cat_pct = round(cat_collected / cat_total * 100, 1) if cat_total > 0 else 0
        lines.append(f"  {cat}: {cat_collected}/{cat_total} collected ({cat_pct}%)")
    lines.append("")

    # Issues
    if report["issues"]:
        lines.append(f"--- Issues ({len(report['issues'])}) ---")
        for issue in report["issues"]:
            ctrl_id = issue.get("control_id", "N/A")
            desc = issue.get("issue", "Unknown issue")
            lines.append(f"  [{ctrl_id}] {desc}")
    else:
        lines.append("--- No Issues Found ---")

    lines.append("")
    return "\n".join(lines)
def main():
    parser = argparse.ArgumentParser(
        description="SOC 2 Evidence Tracker — tracks evidence collection status per control."
    )
    parser.add_argument(
        "--matrix",
        type=str,
        required=True,
        help="Path to JSON control matrix file (from control_matrix_builder.py)",
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Generate evidence collection status report",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format",
    )

    args = parser.parse_args()

    if not args.status:
        parser.print_help()
        print("\nError: --status flag is required.", file=sys.stderr)
        sys.exit(1)

    controls = load_matrix(args.matrix)
    report = generate_status_report(controls)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(format_status_text(report))
