# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from risk_assessment_base import *  # noqa: F403,E402
# fmt: off
from risk_assessment_p1 import load_assets_from_csv  # noqa: E402,E501
from risk_assessment_p2 import assess_risks, generate_sample_assets  # noqa: E402,E501
from risk_assessment_p3 import generate_report  # noqa: E402,E501
# fmt: on


def main():
    parser = argparse.ArgumentParser(
        description="Security Risk Assessment Tool - ISO 27001 Clause 6.1.2"
    )
    parser.add_argument(
        "--scope", "-s",
        required=True,
        help="System or area to assess"
    )
    parser.add_argument(
        "--template", "-t",
        choices=["general", "healthcare", "cloud"],
        default="general",
        help="Assessment template (default: general)"
    )
    parser.add_argument(
        "--assets", "-a",
        help="CSV file with asset inventory"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file path (default: stdout)"
    )
    parser.add_argument(
        "--format", "-f",
        choices=["json", "csv", "markdown"],
        default="markdown",
        help="Output format (default: markdown)"
    )

    args = parser.parse_args()

    # Load or generate assets
    if args.assets:
        assets = load_assets_from_csv(args.assets)
    else:
        assets = generate_sample_assets(args.scope, args.template)

    # Perform risk assessment
    risks = assess_risks(assets, args.template)

    # Generate report
    report = generate_report(
        args.scope,
        args.template,
        assets,
        risks,
        args.format
    )

    # Output
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"Report saved to: {args.output}", file=sys.stderr)
    else:
        print(report)
