# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from dep_scanner_base import *  # noqa: F403,E402


@dataclass
class Vulnerability:
    """Represents a security vulnerability."""
    id: str
    summary: str
    severity: str
    cvss_score: float
    affected_versions: str
    fixed_version: Optional[str]
    published_date: str
    references: List[str]


@dataclass
class Dependency:
    """Represents a project dependency."""
    name: str
    version: str
    ecosystem: str
    direct: bool
    license: Optional[str] = None
    description: Optional[str] = None
    homepage: Optional[str] = None
    vulnerabilities: List[Vulnerability] = None
    
    def __post_init__(self):
        if self.vulnerabilities is None:
            self.vulnerabilities = []


def main():
    """Main entry point for the dependency scanner."""
    parser = argparse.ArgumentParser(
        description='Scan project dependencies for vulnerabilities and security issues',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python dep_scanner.py /path/to/project
  python dep_scanner.py . --format json --output results.json
  python dep_scanner.py /app --fail-on-high
        """
    )
    
    parser.add_argument('project_path', 
                       help='Path to the project directory to scan')
    parser.add_argument('--format', choices=['text', 'json'], default='text',
                       help='Output format (default: text)')
    parser.add_argument('--output', '-o',
                       help='Output file path (default: stdout)')
    parser.add_argument('--fail-on-high', action='store_true',
                       help='Exit with error code if high-severity vulnerabilities found')
    parser.add_argument('--quick-scan', action='store_true',
                       help='Perform quick scan (skip transitive dependencies)')
    
    args = parser.parse_args()
    
    try:
        scanner = DependencyScanner()
        results = scanner.scan_project(args.project_path)
        report = scanner.generate_report(results, args.format)
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(report)
            print(f"Report saved to {args.output}")
        else:
            print(report)
        
        # Exit with error if high-severity vulnerabilities found and --fail-on-high is set
        if args.fail_on_high and results['high_severity_count'] > 0:
            sys.exit(1)
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
