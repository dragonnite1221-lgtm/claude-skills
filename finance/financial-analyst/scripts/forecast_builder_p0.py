# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from forecast_builder_base import *  # noqa: F403,E402


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers, returning default if denominator is zero."""
    if denominator == 0 or denominator is None:
        return default
    return numerator / denominator


def simple_linear_regression(
    x_values: List[float], y_values: List[float]
) -> Tuple[float, float, float]:
    """
    Simple linear regression using standard library.

    Returns (slope, intercept, r_squared).
    """
    n = len(x_values)
    if n < 2 or n != len(y_values):
        return (0.0, 0.0, 0.0)

    x_mean = mean(x_values)
    y_mean = mean(y_values)

    ss_xy = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, y_values))
    ss_xx = sum((x - x_mean) ** 2 for x in x_values)
    ss_yy = sum((y - y_mean) ** 2 for y in y_values)

    slope = safe_divide(ss_xy, ss_xx)
    intercept = y_mean - slope * x_mean

    # R-squared
    r_squared = safe_divide(ss_xy ** 2, ss_xx * ss_yy) if ss_yy > 0 else 0.0

    return (slope, intercept, r_squared)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Driver-based revenue forecasting with scenario modeling"
    )
    parser.add_argument(
        "input_file",
        help="Path to JSON file with forecast data",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--scenarios",
        type=str,
        default="base,bull,bear",
        help="Comma-separated list of scenarios (default: base,bull,bear)",
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

    builder = ForecastBuilder(data)
    scenarios = [s.strip() for s in args.scenarios.split(",")]

    results = builder.run_full_forecast(scenarios)

    if args.format == "json":
        print(json.dumps(results, indent=2))
    else:
        print(builder.format_text(results))
