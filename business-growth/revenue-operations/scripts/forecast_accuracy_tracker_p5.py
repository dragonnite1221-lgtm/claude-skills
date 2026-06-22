# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from forecast_accuracy_tracker_base import *  # noqa: F403,E402
# fmt: off
from forecast_accuracy_tracker_p4 import format_text_report, track_forecast_accuracy  # noqa: E402,E501
# fmt: on


def main() -> None:
    """Main entry point for forecast accuracy tracker CLI."""
    parser = argparse.ArgumentParser(
        description="Track and analyze forecast accuracy for SaaS revenue teams."
    )
    parser.add_argument(
        "input",
        help="Path to JSON file containing forecast data",
    )
    parser.add_argument(
        "--format",
        choices=["json", "text"],
        default="text",
        help="Output format: json or text (default: text)",
    )

    args = parser.parse_args()

    try:
        with open(args.input, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {args.input}: {e}", file=sys.stderr)
        sys.exit(1)

    if "forecast_periods" not in data:
        print("Error: Missing required field 'forecast_periods' in input data", file=sys.stderr)
        sys.exit(1)

    results = track_forecast_accuracy(data)

    if args.format == "json":
        print(json.dumps(results, indent=2))
    else:
        print(format_text_report(results))
