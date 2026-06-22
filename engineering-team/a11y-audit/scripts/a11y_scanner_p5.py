# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from a11y_scanner_base import *  # noqa: F403,E402
# fmt: off
from a11y_scanner_p1 import Finding  # noqa: E402,E501
from a11y_scanner_p4 import collect_files, format_human, format_json, scan_file  # noqa: E402,E501
# fmt: on


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="a11y_scanner",
        description="Scan frontend codebases for WCAG 2.2 accessibility violations.",
        epilog=(
            "Supported file types: .html, .htm, .jsx, .tsx, .vue, .svelte, .css\n"
            "Exit codes: 0 = pass, 1 = critical/serious found, 2 = moderate/minor only"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "path",
        help="File or directory to scan",
    )
    parser.add_argument(
        "--json", dest="json_flag", action="store_true",
        help="Output results as JSON (shorthand for --format json)",
    )
    parser.add_argument(
        "--format", dest="output_format", choices=["text", "json"],
        default="text",
        help="Output format: text (default) or json",
    )
    parser.add_argument(
        "--severity", dest="severity",
        default=None,
        help="Comma-separated severity filter (e.g. critical,serious)",
    )
    return parser
def main():
    parser = build_parser()
    args = parser.parse_args()

    path = os.path.abspath(args.path)
    if not os.path.exists(path):
        print(f"Error: path does not exist: {path}", file=sys.stderr)
        sys.exit(1)

    use_json = args.json_flag or args.output_format == "json"

    # Collect and scan files
    files = collect_files(path)
    if not files:
        print(f"No scannable files found in: {path}", file=sys.stderr)
        sys.exit(0)

    all_findings: List[Finding] = []
    for fpath in files:
        all_findings.extend(scan_file(fpath))

    # Filter by severity if requested
    if args.severity:
        allowed = {s.strip().lower() for s in args.severity.split(",")}
        all_findings = [f for f in all_findings if f.severity in allowed]

    # Output
    if use_json:
        print(format_json(all_findings, len(files)))
    else:
        print(format_human(all_findings, len(files)))

    # Exit code
    severities = {f.severity for f in all_findings}
    if severities & {"critical", "serious"}:
        sys.exit(1)
    elif severities & {"moderate", "minor"}:
        sys.exit(2)
    else:
        sys.exit(0)
