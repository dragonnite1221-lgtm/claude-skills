# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from spec_validator_base import *  # noqa: F403,E402


def format_human(result: Dict[str, Any]) -> str:
    """Format validation result for human reading."""
    lines = [
        "=" * 60,
        "SPEC VALIDATION REPORT",
        "=" * 60,
        "",
    ]
    if result["file"]:
        lines.append(f"File: {result['file']}")
        lines.append("")

    lines.append(result["summary"])

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Validate a feature specification for completeness and quality.",
        epilog="Example: python spec_validator.py --file spec.md --strict",
    )
    parser.add_argument(
        "--file",
        "-f",
        required=True,
        help="Path to the spec markdown file",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with code 2 if score is below 80",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_flag",
        help="Output results as JSON",
    )

    args = parser.parse_args()

    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(2)

    content = file_path.read_text(encoding="utf-8")

    if not content.strip():
        print(f"Error: File is empty: {file_path}", file=sys.stderr)
        sys.exit(2)

    validator = SpecValidator(content, str(file_path))
    result = validator.validate()

    if args.json_flag:
        print(json.dumps(result, indent=2))
    else:
        print(format_human(result))

    # Determine exit code
    score = result["score"]
    has_errors = any(f["severity"] == "error" for f in result["findings"])
    has_warnings = any(f["severity"] == "warning" for f in result["findings"])

    if args.strict and score < 80:
        sys.exit(2)
    elif has_errors:
        sys.exit(2)
    elif has_warnings:
        sys.exit(1)
    else:
        sys.exit(0)
