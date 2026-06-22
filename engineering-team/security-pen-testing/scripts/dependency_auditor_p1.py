# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from dependency_auditor_base import *  # noqa: F403,E402
from dependency_auditor_p0 import format_report_text  # noqa: F401,E501


def main():
    parser = argparse.ArgumentParser(
        description="Dependency Auditor — Analyze package manifests for known vulnerabilities and risky patterns.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Supported manifests:
  package.json      (npm)
  requirements.txt  (pip/PyPI)
  go.mod            (Go)
  Gemfile           (Ruby)

Examples:
  %(prog)s --file package.json
  %(prog)s --file requirements.txt --severity high
  %(prog)s --file go.mod --json
        """,
    )
    parser.add_argument("--file", required=True, metavar="PATH",
                        help="Path to package manifest file")
    parser.add_argument("--severity", choices=["low", "medium", "high", "critical"], default="low",
                        help="Minimum severity to report (default: low)")
    parser.add_argument("--json", action="store_true", dest="json_output",
                        help="Output results as JSON")
    args = parser.parse_args()

    if not Path(args.file).exists():
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    auditor = DependencyAuditor(manifest_path=args.file, severity_filter=args.severity)
    result = auditor.audit()

    if args.json_output:
        json_result = {
            "manifest": result["manifest"],
            "ecosystem": result["ecosystem"],
            "total_dependencies": result["total_dependencies"],
            "dev_dependencies": result["dev_dependencies"],
            "summary": result["summary"],
            "vulnerability_findings": [asdict(f) for f in result["vulnerability_findings"]],
            "risky_patterns": [asdict(r) for r in result["risky_patterns"]],
            "generated_at": datetime.now().isoformat(),
        }
        print(json.dumps(json_result, indent=2))
    else:
        print(format_report_text(result))

    # Exit non-zero if critical or high vulnerabilities found
    if result["summary"]["critical"] > 0 or result["summary"]["high"] > 0:
        sys.exit(1)
