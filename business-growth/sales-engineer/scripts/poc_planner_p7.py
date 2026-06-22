# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from poc_planner_base import *  # noqa: F403,E402
# fmt: off
from poc_planner_p1 import load_poc_data  # noqa: E402,E501
from poc_planner_p5 import plan_poc  # noqa: E402,E501
from poc_planner_p6 import format_text  # noqa: E402,E501
# fmt: on


def main() -> None:
    """Main entry point for the POC Planner."""
    parser = argparse.ArgumentParser(
        description="Plan proof-of-concept engagements with timeline, resources, and evaluation scorecards.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Default Phases:\n"
            "  Week 1:   Setup - Environment provisioning, configuration\n"
            "  Weeks 2-3: Core Testing - Primary use cases, integrations\n"
            "  Week 4:   Advanced Testing - Edge cases, performance, security\n"
            "  Week 5:   Evaluation - Scorecard, stakeholder review, go/no-go\n"
            "\n"
            "Example:\n"
            "  python poc_planner.py poc_data.json --format json\n"
        ),
    )
    parser.add_argument(
        "input_file",
        help="Path to JSON file containing POC scope and requirements",
    )
    parser.add_argument(
        "--format",
        choices=["json", "text"],
        default="text",
        dest="output_format",
        help="Output format: json or text (default: text)",
    )

    args = parser.parse_args()

    data = load_poc_data(args.input_file)
    result = plan_poc(data)

    if args.output_format == "json":
        print(json.dumps(result, indent=2))
    else:
        print(format_text(result))
