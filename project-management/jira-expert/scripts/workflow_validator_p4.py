# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from workflow_validator_base import *  # noqa: F403,E402
# fmt: off
from workflow_validator_p3 import format_json_output, format_text_output, validate_workflow  # noqa: E402,E501
# fmt: on


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Validate Jira workflow definitions for anti-patterns"
    )
    parser.add_argument(
        "workflow_file",
        help="JSON file containing workflow definition (states, transitions)",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )

    args = parser.parse_args()

    try:
        with open(args.workflow_file, "r") as f:
            data = json.load(f)

        result = validate_workflow(data)

        if args.format == "json":
            print(json.dumps(format_json_output(result), indent=2))
        else:
            print(format_text_output(result))

        return 0

    except FileNotFoundError:
        print(f"Error: File '{args.workflow_file}' not found", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in '{args.workflow_file}': {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
