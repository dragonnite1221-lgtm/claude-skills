# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from isms_audit_scheduler_base import *  # noqa: F403,E402
# fmt: off
from isms_audit_scheduler_p1 import load_controls_from_csv  # noqa: E402,E501
from isms_audit_scheduler_p2 import format_markdown, generate_audit_plan  # noqa: E402,E501
# fmt: on


def main():
    parser = argparse.ArgumentParser(
        description="ISMS Audit Scheduler - Risk-based audit planning"
    )
    parser.add_argument(
        "--year", "-y",
        type=int,
        default=datetime.now().year,
        help="Audit plan year (default: current year)"
    )
    parser.add_argument(
        "--controls", "-c",
        help="CSV file with control risk ratings"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file path"
    )
    parser.add_argument(
        "--format", "-f",
        choices=["json", "markdown"],
        default="json",
        help="Output format (default: json)"
    )

    args = parser.parse_args()

    # Load controls
    controls = None
    if args.controls:
        controls = load_controls_from_csv(args.controls)

    # Generate plan
    plan = generate_audit_plan(args.year, controls)

    # Format output
    if args.format == "markdown":
        output = format_markdown(plan)
    else:
        output = json.dumps(plan, indent=2)

    # Write output
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Audit plan saved to: {args.output}", file=sys.stderr)
    else:
        print(output)
