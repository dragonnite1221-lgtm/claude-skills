# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from dependency_analyzer_base import *  # noqa: F403,E402
from dependency_analyzer_p0 import print_human_report  # noqa: F401,E501


def main():
    parser = argparse.ArgumentParser(
        description='Analyze project dependencies and module coupling',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s ./my-project
  %(prog)s ./my-project --output json
  %(prog)s ./my-project --check circular
  %(prog)s ./my-project --verbose

Supported package managers:
  - npm/yarn (package.json)
  - pip (requirements.txt)
  - poetry (pyproject.toml)
  - go (go.mod)
  - cargo (Cargo.toml)
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
        choices=['all', 'circular', 'coupling'],
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
    analyzer = DependencyAnalyzer(project_path, verbose=args.verbose)
    report = analyzer.analyze()

    # Filter report based on --check option
    if args.check == 'circular':
        if report['circular_dependencies']:
            print("Circular dependencies found:")
            for cycle in report['circular_dependencies']:
                print(f"  {' -> '.join(cycle)}")
            sys.exit(1)
        else:
            print("No circular dependencies found.")
            sys.exit(0)
    elif args.check == 'coupling':
        score = report['summary']['coupling_score']
        print(f"Coupling score: {score}/100")
        if score > 70:
            print("WARNING: High coupling detected")
            sys.exit(1)
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
