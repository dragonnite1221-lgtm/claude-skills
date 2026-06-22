# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from compliance_checker_base import *  # noqa: F403,E402


@dataclass
class ComplianceControl:
    """Represents a compliance control check result."""
    control_id: str
    framework: str
    category: str
    title: str
    description: str
    status: str  # passed, failed, warning, not_applicable
    evidence: List[str]
    recommendation: str
    severity: str  # critical, high, medium, low


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="Check compliance against SOC 2, PCI-DSS, HIPAA, GDPR",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /path/to/project
  %(prog)s /path/to/project --framework soc2
  %(prog)s /path/to/project --framework pci-dss --output report.json
  %(prog)s . --framework all --verbose
        """
    )

    parser.add_argument(
        "target",
        help="Directory to check for compliance"
    )
    parser.add_argument(
        "--framework", "-f",
        choices=["soc2", "pci-dss", "hipaa", "gdpr", "all"],
        default="all",
        help="Compliance framework to check (default: all)"
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

    checker = ComplianceChecker(
        target_path=args.target,
        framework=args.framework,
        verbose=args.verbose
    )

    result = checker.check()

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

    # Exit with error code based on compliance level
    if result.get('compliance_level') == 'CRITICAL_GAPS':
        sys.exit(2)
    if result.get('compliance_level') == 'NON_COMPLIANT':
        sys.exit(1)
