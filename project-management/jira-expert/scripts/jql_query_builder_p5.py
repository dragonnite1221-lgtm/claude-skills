# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from jql_query_builder_base import *  # noqa: F403,E402
# fmt: off
from jql_query_builder_p3 import build_jql_from_description  # noqa: E402,E501
from jql_query_builder_p4 import format_json_output, format_patterns_output, format_text_output, validate_jql_syntax  # noqa: E402,E501
# fmt: on


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Build JQL queries from natural language descriptions"
    )
    parser.add_argument(
        "description",
        nargs="?",
        help="Natural language description of the query",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--patterns",
        action="store_true",
        help="List all available query patterns",
    )

    args = parser.parse_args()

    try:
        if args.patterns:
            print(format_patterns_output(args.format))
            return 0

        if not args.description:
            parser.error("description is required unless --patterns is used")

        # Build query
        result = build_jql_from_description(args.description)

        # Validate
        if result.get("jql"):
            result["validation"] = validate_jql_syntax(result["jql"])

        # Output results
        if args.format == "json":
            output = format_json_output(result)
            print(json.dumps(output, indent=2))
        else:
            output = format_text_output(result)
            print(output)

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
