# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from competitive_matrix_builder_base import *  # noqa: F403,E402
# fmt: off
from competitive_matrix_builder_p1 import load_competitive_data  # noqa: E402,E501
from competitive_matrix_builder_p4 import analyze_competitive  # noqa: E402,E501
from competitive_matrix_builder_p5 import format_text  # noqa: E402,E501
# fmt: on


def main() -> None:
    """Main entry point for the Competitive Matrix Builder."""
    parser = argparse.ArgumentParser(
        description="Build competitive feature comparison matrices and positioning analysis.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Feature Scoring:\n"
            "  Full (3)    - Complete feature support\n"
            "  Partial (2) - Partial or limited support\n"
            "  Limited (1) - Minimal or basic support\n"
            "  None (0)    - Feature not available\n"
            "\n"
            "Example:\n"
            "  python competitive_matrix_builder.py competitive_data.json --format json\n"
        ),
    )
    parser.add_argument(
        "input_file",
        help="Path to JSON file containing competitive data",
    )
    parser.add_argument(
        "--format",
        choices=["json", "text"],
        default="text",
        dest="output_format",
        help="Output format: json or text (default: text)",
    )

    args = parser.parse_args()

    data = load_competitive_data(args.input_file)
    result = analyze_competitive(data)

    if args.output_format == "json":
        print(json.dumps(result, indent=2))
    else:
        print(format_text(result))
