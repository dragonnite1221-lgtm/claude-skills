# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from campaign_roi_calculator_base import *  # noqa: F403,E402
# fmt: off
from campaign_roi_calculator_p2 import calculate_campaign_metrics  # noqa: E402,E501
from campaign_roi_calculator_p3 import calculate_portfolio_summary  # noqa: E402,E501
from campaign_roi_calculator_p4 import format_text  # noqa: E402,E501
# fmt: on


def main() -> None:
    """Main entry point for the campaign ROI calculator."""
    parser = argparse.ArgumentParser(
        description="Calculate campaign ROI, ROAS, CPA, CPL, CAC with industry benchmarking.",
        epilog="Example: python campaign_roi_calculator.py campaigns.json --format json",
    )
    parser.add_argument(
        "input_file",
        help="Path to JSON file containing campaign data",
    )
    parser.add_argument(
        "--format",
        choices=["json", "text"],
        default="text",
        dest="output_format",
        help="Output format (default: text)",
    )

    args = parser.parse_args()

    # Load input data
    try:
        with open(args.input_file, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {args.input_file}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {args.input_file}: {e}", file=sys.stderr)
        sys.exit(1)

    campaigns = data.get("campaigns", [])
    if not campaigns:
        print("Error: No 'campaigns' array found in input data.", file=sys.stderr)
        sys.exit(1)

    # Calculate metrics for each campaign
    campaign_results = [calculate_campaign_metrics(c) for c in campaigns]

    # Calculate portfolio summary
    portfolio_summary = calculate_portfolio_summary(campaign_results)

    results = {
        "portfolio_summary": portfolio_summary,
        "campaigns": campaign_results,
    }

    if args.output_format == "json":
        print(json.dumps(results, indent=2))
    else:
        print(format_text(results))
