# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from incident_timeline_builder_base import *  # noqa: F403,E402
# fmt: off
from incident_timeline_builder_p3 import build_timeline  # noqa: E402,E501
from incident_timeline_builder_p4 import format_json_output, format_text_output  # noqa: E402,E501
from incident_timeline_builder_p5 import format_markdown_output  # noqa: E402,E501
# fmt: on


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Build structured incident timelines with phase detection and communication templates."
    )
    parser.add_argument(
        "data_file", nargs="?", default=None,
        help="JSON file with incident data (reads stdin if omitted)",
    )
    parser.add_argument(
        "--format", choices=["text", "json", "markdown"], default="text",
        help="Output format (default: text)",
    )
    args = parser.parse_args()

    try:
        if args.data_file:
            try:
                with open(args.data_file, "r") as f:
                    raw_data = json.load(f)
            except FileNotFoundError:
                print(f"Error: File '{args.data_file}' not found.", file=sys.stderr)
                return 1
            except json.JSONDecodeError as e:
                print(f"Error: Invalid JSON in '{args.data_file}': {e}", file=sys.stderr)
                return 1
        else:
            if sys.stdin.isatty():
                print("Error: No input file specified and stdin is a terminal. "
                      "Provide a file argument or pipe JSON to stdin.", file=sys.stderr)
                return 1
            try:
                raw_data = json.load(sys.stdin)
            except json.JSONDecodeError as e:
                print(f"Error: Invalid JSON on stdin: {e}", file=sys.stderr)
                return 1

        if not isinstance(raw_data, dict):
            print("Error: Input must be a JSON object.", file=sys.stderr)
            return 1
        if "incident" not in raw_data and "events" not in raw_data:
            print("Error: Input must contain at least 'incident' or 'events' keys.", file=sys.stderr)
            return 1

        analysis = build_timeline(raw_data)

        if args.format == "json":
            print(json.dumps(format_json_output(analysis), indent=2))
        elif args.format == "markdown":
            print(format_markdown_output(analysis))
        else:
            print(format_text_output(analysis))
        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
