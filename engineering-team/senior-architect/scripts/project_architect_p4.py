# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from project_architect_base import *  # noqa: F403,E402
from project_architect_p2 import ProjectArchitect  # noqa: F401,E501
from project_architect_p3 import print_human_report  # noqa: F401,E501


def main():
    parser = argparse.ArgumentParser(
        description='Analyze project architecture and detect patterns and issues',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s ./my-project
  %(prog)s ./my-project --verbose
  %(prog)s ./my-project --output json
  %(prog)s ./my-project --check layers

Detects:
  - Architectural patterns (Layered, MVC, Hexagonal, Clean, Microservices)
  - Code organization issues (large files, god classes)
  - Layer violations (incorrect dependencies between layers)
  - Missing architectural components
        '''
    )

    parser.add_argument(
        'project_path',
        help='Path to the project directory'
    )
    parser.add_argument(
        '--output', '-o',
        choices=['human', 'json'],
        default='human',
        help='Output format (default: human)'
    )
    parser.add_argument(
        '--check',
        choices=['all', 'pattern', 'layers', 'code'],
        default='all',
        help='What to check (default: all)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    parser.add_argument(
        '--save', '-s',
        help='Save report to file'
    )

    args = parser.parse_args()

    project_path = Path(args.project_path).resolve()
    if not project_path.exists():
        print(f"Error: Project path does not exist: {project_path}", file=sys.stderr)
        sys.exit(1)

    if not project_path.is_dir():
        print(f"Error: Project path is not a directory: {project_path}", file=sys.stderr)
        sys.exit(1)

    # Run analysis
    architect = ProjectArchitect(project_path, verbose=args.verbose)
    report = architect.analyze()

    # Handle specific checks
    if args.check == 'pattern':
        arch = report['architecture']
        print(f"Pattern: {arch['detected_pattern']} (confidence: {arch['confidence']}%)")
        sys.exit(0)
    elif args.check == 'layers':
        violations = report['layer_violations']
        if violations:
            print(f"Found {len(violations)} layer violation(s):")
            for v in violations:
                print(f"  {v['file']}: {v['message']}")
            sys.exit(1)
        else:
            print("No layer violations found.")
            sys.exit(0)
    elif args.check == 'code':
        issues = report['code_quality']['issues']
        if issues:
            print(f"Found {len(issues)} code issue(s):")
            for issue in issues[:10]:
                print(f"  [{issue['severity'].upper()}] {issue['message']}")
            sys.exit(1 if any(i['severity'] == 'warning' for i in issues) else 0)
        else:
            print("No code issues found.")
            sys.exit(0)

    # Output report
    if args.output == 'json':
        output = json.dumps(report, indent=2)
        if args.save:
            Path(args.save).write_text(output)
            print(f"Report saved to {args.save}")
        else:
            print(output)
    else:
        print_human_report(report)
        if args.save:
            Path(args.save).write_text(json.dumps(report, indent=2))
            print(f"\nJSON report saved to {args.save}")
