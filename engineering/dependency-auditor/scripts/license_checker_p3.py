# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from license_checker_base import *  # noqa: F403,E402


def main():
    """Main entry point for the license checker."""
    parser = argparse.ArgumentParser(
        description='Analyze dependency licenses for compliance and conflicts',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python license_checker.py /path/to/project
  python license_checker.py . --format json --output compliance.json
  python license_checker.py /app --inventory deps.json --policy strict
        """
    )
    
    parser.add_argument('project_path',
                       help='Path to the project directory to analyze')
    parser.add_argument('--inventory',
                       help='Path to dependency inventory JSON file')
    parser.add_argument('--format', choices=['text', 'json'], default='text',
                       help='Output format (default: text)')
    parser.add_argument('--output', '-o',
                       help='Output file path (default: stdout)')
    parser.add_argument('--policy', choices=['permissive', 'strict'], default='permissive',
                       help='License policy strictness (default: permissive)')
    parser.add_argument('--warn-conflicts', action='store_true',
                       help='Show warnings for potential conflicts')
    
    args = parser.parse_args()
    
    try:
        checker = LicenseChecker()
        results = checker.analyze_project(args.project_path, args.inventory)
        report = checker.generate_report(results, args.format)
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(report)
            print(f"Compliance report saved to {args.output}")
        else:
            print(report)
        
        # Exit with error code for policy violations
        if args.policy == 'strict' and results['compliance_score'] < 80:
            sys.exit(1)
        
        if args.warn_conflicts and results['conflicts']:
            print("\nWARNING: License conflicts detected!")
            sys.exit(2)
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
