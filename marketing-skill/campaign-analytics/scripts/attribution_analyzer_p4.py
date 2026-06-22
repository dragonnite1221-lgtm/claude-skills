# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from attribution_analyzer_base import *  # noqa: F403,E402
# fmt: off
from attribution_analyzer_p1 import MODELS  # noqa: E402,E501
from attribution_analyzer_p2 import compute_summary, run_model  # noqa: E402,E501
from attribution_analyzer_p3 import format_text  # noqa: E402,E501
# fmt: on


def main() -> None:
    """Main entry point for the attribution analyzer."""
    parser = argparse.ArgumentParser(
        description="Multi-touch attribution analyzer for marketing campaigns.",
        epilog="Example: python attribution_analyzer.py data.json --model linear --format json",
    )
    parser.add_argument(
        "input_file",
        help="Path to JSON file containing journey/touchpoint data",
    )
    parser.add_argument(
        "--model",
        choices=MODELS,
        default=None,
        help="Run a specific attribution model (default: run all 5 models)",
    )
    parser.add_argument(
        "--half-life",
        type=float,
        default=7.0,
        help="Half-life in days for time-decay model (default: 7)",
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

    journeys = data.get("journeys", [])
    if not journeys:
        print("Error: No 'journeys' array found in input data.", file=sys.stderr)
        sys.exit(1)

    # Determine which models to run
    models_to_run = [args.model] if args.model else MODELS

    # Run models
    model_results: Dict[str, Dict[str, float]] = {}
    for model_name in models_to_run:
        credits = run_model(model_name, journeys, args.half_life)
        model_results[model_name] = {ch: round(v, 2) for ch, v in credits.items()}

    # Build output
    results: Dict[str, Any] = {
        "summary": compute_summary(journeys),
        "models": model_results,
    }

    if args.output_format == "json":
        print(json.dumps(results, indent=2))
    else:
        print(format_text(results))
