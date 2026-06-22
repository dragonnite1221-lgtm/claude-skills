# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from secret_scanner_base import *  # noqa: F403,E402
# fmt: off
from secret_scanner_p1 import Severity  # noqa: E402,E501
from secret_scanner_p3 import SECRET_PATTERNS, scan_file  # noqa: E402,E501
from secret_scanner_p4 import format_json_report, format_text_report, list_patterns, scan_directory  # noqa: E402,E501
# fmt: on


def main():
    parser = argparse.ArgumentParser(
        description="Secret Scanner - Detect hardcoded secrets in code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan a project directory
  python secret_scanner.py /path/to/project

  # Scan a single file
  python secret_scanner.py /path/to/config.py

  # Output as JSON
  python secret_scanner.py /path/to/project --format json

  # List all detection patterns
  python secret_scanner.py --list-patterns

  # Save report to file
  python secret_scanner.py /path/to/project --output report.txt
        """
    )

    parser.add_argument(
        "path",
        nargs="?",
        help="Path to scan (file or directory)"
    )
    parser.add_argument(
        "--format", "-f",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file path"
    )
    parser.add_argument(
        "--list-patterns", "-l",
        action="store_true",
        help="List all detection patterns"
    )
    parser.add_argument(
        "--severity", "-s",
        choices=["critical", "high", "medium", "low"],
        help="Minimum severity to report"
    )

    args = parser.parse_args()

    if args.list_patterns:
        list_patterns()
        return

    if not args.path:
        parser.error("path is required (or use --list-patterns)")

    path = Path(args.path)
    if not path.exists():
        print(f"Error: Path does not exist: {path}")
        sys.exit(1)

    # Filter patterns by severity
    patterns = SECRET_PATTERNS
    if args.severity:
        severity_order = ["critical", "high", "medium", "low"]
        min_index = severity_order.index(args.severity)
        allowed = set(Severity(s) for s in severity_order[:min_index + 1])
        patterns = [p for p in patterns if p.severity in allowed]

    # Scan
    if path.is_file():
        findings = scan_file(path, patterns)
    else:
        findings = scan_directory(path, patterns)

    # Format output
    if args.format == "json":
        output = json.dumps(format_json_report(findings, str(path)), indent=2)
    else:
        output = format_text_report(findings, str(path))

    # Write output
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"Report written to {args.output}")
    else:
        print(output)

    # Exit code based on findings
    if any(f.severity in (Severity.CRITICAL, Severity.HIGH) for f in findings):
        sys.exit(1)
