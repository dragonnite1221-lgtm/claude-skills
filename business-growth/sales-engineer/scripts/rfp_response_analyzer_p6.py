# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from rfp_response_analyzer_base import *  # noqa: F403,E402
# fmt: off
from rfp_response_analyzer_p1 import load_rfp_data  # noqa: E402,E501
from rfp_response_analyzer_p4 import analyze_rfp  # noqa: E402,E501
from rfp_response_analyzer_p5 import format_text  # noqa: E402,E501
# fmt: on


def main() -> None:
    """Main entry point for the RFP Response Analyzer."""
    parser = argparse.ArgumentParser(
        description="Analyze RFP/RFI requirements for coverage, gaps, and bid recommendation.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Coverage Categories:\n"
            "  Full (100%)    - Requirement fully met\n"
            "  Partial (50%)  - Partially met, workaround needed\n"
            "  Planned (25%)  - On roadmap, not yet available\n"
            "  Gap (0%)       - Not supported\n"
            "\n"
            "Priority Weights:\n"
            "  Must-Have (3x) | Should-Have (2x) | Nice-to-Have (1x)\n"
            "\n"
            "Example:\n"
            "  python rfp_response_analyzer.py rfp_data.json --format json\n"
        ),
    )
    parser.add_argument(
        "input_file",
        help="Path to JSON file containing RFP requirements data",
    )
    parser.add_argument(
        "--format",
        choices=["json", "text"],
        default="text",
        dest="output_format",
        help="Output format: json or text (default: text)",
    )

    args = parser.parse_args()

    data = load_rfp_data(args.input_file)
    result = analyze_rfp(data)

    if args.output_format == "json":
        print(json.dumps(result, indent=2))
    else:
        print(format_text(result))
