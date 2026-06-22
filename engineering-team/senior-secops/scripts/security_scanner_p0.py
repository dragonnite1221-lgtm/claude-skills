# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from security_scanner_base import *  # noqa: F403,E402


@dataclass
class SecurityFinding:
    """Represents a security finding."""
    rule_id: str
    severity: str  # critical, high, medium, low, info
    category: str
    title: str
    description: str
    file_path: str
    line_number: int
    code_snippet: str
    recommendation: str


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="Scan source code for security vulnerabilities",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /path/to/project
  %(prog)s /path/to/project --severity high
  %(prog)s /path/to/project --output report.json --json
  %(prog)s /path/to/file.py --verbose
        """
    )

    parser.add_argument(
        "target",
        help="Directory or file to scan"
    )
    parser.add_argument(
        "--severity", "-s",
        choices=["critical", "high", "medium", "low", "info"],
        default="low",
        help="Minimum severity to report (default: low)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file path"
    )

    args = parser.parse_args()

    scanner = SecurityScanner(
        target_path=args.target,
        severity_threshold=args.severity,
        verbose=args.verbose
    )

    result = scanner.scan()

    if args.json:
        output = json.dumps(result, indent=2)
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
            print(f"\nResults written to {args.output}")
        else:
            print(output)
    elif args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\nResults written to {args.output}")

    # Exit with error code if critical/high findings
    if result.get('severity_counts', {}).get('critical', 0) > 0:
        sys.exit(2)
    if result.get('severity_counts', {}).get('high', 0) > 0:
        sys.exit(1)
