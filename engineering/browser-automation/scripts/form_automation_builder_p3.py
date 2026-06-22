# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from form_automation_builder_base import *  # noqa: F403,E402
# fmt: off
from form_automation_builder_p2 import build_form_script  # noqa: E402,E501
# fmt: on


def main():
    parser = argparse.ArgumentParser(
        description="Generate Playwright form-fill automation scripts from a JSON field specification.",
        epilog=textwrap.dedent("""\
Examples:
  %(prog)s --url https://example.com/signup --fields fields.json
  %(prog)s --url https://example.com/signup --fields fields.json --output fill_form.py
  %(prog)s --url https://example.com/signup --fields fields.json --json

Field specification format (fields.json):
  [
    {"selector": "#email", "type": "email", "value": "user@example.com", "label": "Email"},
    {"selector": "#password", "type": "password", "value": "s3cret"},
    {"selector": "#country", "type": "select", "value": "US"},
    {"selector": "#terms", "type": "checkbox", "value": "true"},
    {"selector": "#avatar", "type": "file", "value": "/path/to/photo.jpg"},
    {"selector": "button[type='submit']", "type": "click", "is_submit": true}
  ]

Supported field types: text, password, email, textarea, select, checkbox, radio, file, click

Multi-step forms: Add "step": N to each field to group into steps.
        """),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--url",
        required=True,
        help="Target form URL",
    )
    parser.add_argument(
        "--fields",
        required=True,
        help="Path to JSON file containing field specifications",
    )
    parser.add_argument(
        "--output",
        help="Output file path (default: stdout)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        default=False,
        help="Output JSON configuration instead of Python script",
    )

    args = parser.parse_args()

    # Load fields
    fields_path = os.path.abspath(args.fields)
    if not os.path.isfile(fields_path):
        print(f"Error: Fields file not found: {fields_path}", file=sys.stderr)
        sys.exit(2)

    try:
        with open(fields_path, "r") as f:
            fields = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {fields_path}: {e}", file=sys.stderr)
        sys.exit(2)

    output_format = "json" if args.json_output else "script"
    result, errors = build_form_script(
        url=args.url,
        fields=fields,
        output_format=output_format,
    )

    if errors:
        print("Validation errors:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        sys.exit(2)

    if args.json_output:
        output_text = json.dumps(result, indent=2)
    else:
        output_text = result

    if args.output:
        output_path = os.path.abspath(args.output)
        with open(output_path, "w") as f:
            f.write(output_text)
        if not args.json_output:
            os.chmod(output_path, 0o755)
        print(f"Written to {output_path}", file=sys.stderr)
        sys.exit(0)
    else:
        print(output_text)
        sys.exit(0)
