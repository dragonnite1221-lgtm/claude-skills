# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from compliance_checker_base import *  # noqa: F403,E402
# fmt: off
from compliance_checker_p1 import load_controls_from_csv  # noqa: E402,E501
from compliance_checker_p2 import check_compliance  # noqa: E402,E501
from compliance_checker_p3 import format_output  # noqa: E402,E501
# fmt: on


def main():
    parser = argparse.ArgumentParser(
        description="ISO 27001/27002 Compliance Checker"
    )
    parser.add_argument(
        "--standard", "-s",
        required=True,
        choices=["iso27001", "iso27002", "hipaa"],
        help="Compliance standard to check"
    )
    parser.add_argument(
        "--controls-file", "-c",
        help="CSV file with current control implementation status"
    )
    parser.add_argument(
        "--gap-analysis", "-g",
        action="store_true",
        help="Include gap analysis with remediation recommendations"
    )
    parser.add_argument(
        "--domains", "-d",
        help="Comma-separated list of domains to check (e.g., organizational,technological)"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file path (default: stdout)"
    )
    parser.add_argument(
        "--format", "-f",
        choices=["json", "markdown"],
        default="markdown",
        help="Output format (default: markdown)"
    )

    args = parser.parse_args()

    # Load control status if provided
    controls_data = None
    if args.controls_file:
        controls_data = load_controls_from_csv(args.controls_file)

    # Parse domains
    domains = None
    if args.domains:
        domains = [d.strip().lower().replace("-", "_") for d in args.domains.split(",")]

    # Check compliance
    results = check_compliance(args.standard, controls_data, domains)

    # Format output
    output = format_output(results, args.gap_analysis, args.format)

    # Write output
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Report saved to: {args.output}", file=sys.stderr)
    else:
        print(output)
