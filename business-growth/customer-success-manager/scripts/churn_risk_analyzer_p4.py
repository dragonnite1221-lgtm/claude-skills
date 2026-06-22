# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from churn_risk_analyzer_base import *  # noqa: F403,E402
# fmt: off
from churn_risk_analyzer_p3 import analyse_churn_risk, format_json, format_text  # noqa: E402,E501
# fmt: on


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyse churn risk with behavioral signal detection and intervention recommendations."
    )
    parser.add_argument("input_file", help="Path to JSON file containing customer data")
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        dest="output_format",
        help="Output format (default: text)",
    )
    args = parser.parse_args()

    try:
        with open(args.input_file, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {args.input_file}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {args.input_file}: {e}", file=sys.stderr)
        sys.exit(1)

    customers = data.get("customers", [])
    if not customers:
        print("Error: No customer records found in input file.", file=sys.stderr)
        sys.exit(1)

    results = [analyse_churn_risk(c) for c in customers]

    if args.output_format == "json":
        print(format_json(results))
    else:
        print(format_text(results))
