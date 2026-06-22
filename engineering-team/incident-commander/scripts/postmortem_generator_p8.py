# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from postmortem_generator_base import *  # noqa: F403,E402
# fmt: off
from postmortem_generator_p4 import PostmortemReport  # noqa: E402,E501
from postmortem_generator_p6 import format_json, format_text  # noqa: E402,E501
from postmortem_generator_p7 import format_markdown  # noqa: E402,E501
# fmt: on


def load_input(filepath: Optional[str]) -> Dict[str, Any]:
    """Load incident data from a file path or stdin."""
    if filepath:
        try:
            with open(filepath, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except FileNotFoundError:
            print(f"Error: File not found: {filepath}", file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError as exc:
            print(f"Error: Invalid JSON in {filepath}: {exc}", file=sys.stderr)
            sys.exit(1)
    else:
        if sys.stdin.isatty():
            print("Error: No input file specified and no data on stdin.", file=sys.stderr)
            print("Usage: postmortem_generator.py [data_file] or pipe JSON via stdin.", file=sys.stderr)
            sys.exit(1)
        try:
            return json.load(sys.stdin)
        except json.JSONDecodeError as exc:
            print(f"Error: Invalid JSON on stdin: {exc}", file=sys.stderr)
            sys.exit(1)
def validate_input(data: Dict[str, Any]) -> List[str]:
    """Return a list of validation warnings (non-fatal)."""
    warnings: List[str] = []
    for key in ("incident", "timeline", "resolution", "action_items"):
        if key not in data:
            warnings.append(f"Missing '{key}' section")
    for ts in ("issue_started", "detected_at", "mitigated_at", "resolved_at"):
        if ts not in data.get("timeline", {}):
            warnings.append(f"Missing timeline field: {ts}")
    res = data.get("resolution", {})
    if "root_cause" not in res:
        warnings.append("Missing 'root_cause' in resolution")
    if not res.get("contributing_factors"):
        warnings.append("No contributing factors provided")
    return warnings
def main() -> None:
    """CLI entry point for postmortem generation."""
    parser = argparse.ArgumentParser(
        description="Generate structured postmortem reports with 5-Whys analysis.",
        epilog="Reads JSON from a file or stdin. Outputs text, JSON, or markdown.")
    parser.add_argument("data_file", nargs="?", default=None,
                        help="JSON file with incident + resolution data (reads stdin if omitted)")
    parser.add_argument("--format", choices=["text", "json", "markdown"], default="text",
                        dest="output_format", help="Output format (default: text)")
    args = parser.parse_args()

    data = load_input(args.data_file)
    warnings = validate_input(data)
    for w in warnings:
        print(f"Warning: {w}", file=sys.stderr)

    report = PostmortemReport(data)
    formatters = {"text": format_text, "json": format_json, "markdown": format_markdown}
    print(formatters[args.output_format](report))
