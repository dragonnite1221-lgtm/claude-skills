# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from ratio_calculator_base import *  # noqa: F403,E402


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers, returning default if denominator is zero."""
    if denominator == 0 or denominator is None:
        return default
    return numerator / denominator


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Calculate and interpret financial ratios"
    )
    parser.add_argument(
        "input_file",
        help="Path to JSON file with financial statement data",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--category",
        choices=[
            "profitability",
            "liquidity",
            "leverage",
            "efficiency",
            "valuation",
        ],
        default=None,
        help="Calculate only a specific ratio category",
    )

    args = parser.parse_args()

    try:
        with open(args.input_file, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File '{args.input_file}' not found.", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in '{args.input_file}': {e}", file=sys.stderr)
        sys.exit(1)

    calculator = FinancialRatioCalculator(data)

    if args.category:
        method_map = {
            "profitability": calculator.calculate_profitability,
            "liquidity": calculator.calculate_liquidity,
            "leverage": calculator.calculate_leverage,
            "efficiency": calculator.calculate_efficiency,
            "valuation": calculator.calculate_valuation,
        }
        method_map[args.category]()
    else:
        calculator.calculate_all()

    if args.format == "json":
        print(json.dumps(calculator.to_json(args.category), indent=2))
    else:
        print(calculator.format_text(args.category))
