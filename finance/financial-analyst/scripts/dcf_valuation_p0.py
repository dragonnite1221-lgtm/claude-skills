# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from dcf_valuation_base import *  # noqa: F403,E402


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers, returning default if denominator is zero."""
    if denominator == 0 or denominator is None:
        return default
    return numerator / denominator


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="DCF Valuation Model - Enterprise and equity valuation"
    )
    parser.add_argument(
        "input_file",
        help="Path to JSON file with valuation data",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--projection-years",
        type=int,
        default=None,
        help="Number of projection years (overrides input file)",
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

    model = DCFModel()
    model.set_historical_financials(data.get("historical", {}))

    assumptions = data.get("assumptions", {})
    if args.projection_years is not None:
        assumptions["projection_years"] = args.projection_years
    model.set_assumptions(assumptions)

    try:
        results = model.run_full_valuation()
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.format == "json":
        # Handle inf values for JSON serialization
        def sanitize(obj: Any) -> Any:
            if isinstance(obj, float) and math.isinf(obj):
                return None
            if isinstance(obj, dict):
                return {k: sanitize(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [sanitize(v) for v in obj]
            return obj

        print(json.dumps(sanitize(results), indent=2))
    else:
        print(model.format_text(results))
