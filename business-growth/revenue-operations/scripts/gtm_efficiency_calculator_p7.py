# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from gtm_efficiency_calculator_base import *  # noqa: F403,E402
# fmt: off
from gtm_efficiency_calculator_p5 import calculate_all_metrics  # noqa: E402,E501
from gtm_efficiency_calculator_p6 import format_text_report  # noqa: E402,E501
# fmt: on


def main() -> None:
    """Main entry point for GTM efficiency calculator CLI."""
    parser = argparse.ArgumentParser(
        description="Calculate GTM efficiency metrics for SaaS revenue teams."
    )
    parser.add_argument(
        "input",
        help="Path to JSON file containing GTM data",
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

    required_sections = ["revenue", "costs", "customers"]
    for section in required_sections:
        if section not in data:
            print(
                f"Error: Missing required section '{section}' in input data",
                file=sys.stderr,
            )
            sys.exit(1)

    results = calculate_all_metrics(data)

    if args.format == "json":
        print(json.dumps(results, indent=2))
    else:
        print(format_text_report(results))
