# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from budget_variance_analyzer_base import *  # noqa: F403,E402


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers, returning default if denominator is zero."""
    if denominator == 0 or denominator is None:
        return default
    return numerator / denominator


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze budget variances with materiality filtering"
    )
    parser.add_argument(
        "input_file",
        help="Path to JSON file with budget data",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--threshold-pct",
        type=float,
        default=10.0,
        help="Materiality threshold percentage (default: 10)",
    )
    parser.add_argument(
        "--threshold-amt",
        type=float,
        default=50000.0,
        help="Materiality threshold dollar amount (default: 50000)",
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

    analyzer = BudgetVarianceAnalyzer(
        data,
        threshold_pct=args.threshold_pct,
        threshold_amt=args.threshold_amt,
    )

    results = analyzer.run_analysis()

    if args.format == "json":
        print(json.dumps(results, indent=2))
    else:
        print(analyzer.format_text(results))
