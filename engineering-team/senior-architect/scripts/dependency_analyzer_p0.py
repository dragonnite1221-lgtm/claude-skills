# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from dependency_analyzer_base import *  # noqa: F403,E402


def print_human_report(report: Dict):
    """Print human-readable report."""
    print("\n" + "=" * 60)
    print("DEPENDENCY ANALYSIS REPORT")
    print("=" * 60)
    print(f"\nProject: {report['project_path']}")
    print(f"Package Manager: {report['package_manager']}")

    summary = report['summary']
    print("\n--- Summary ---")
    print(f"Direct dependencies: {summary['direct_dependencies']}")
    print(f"Dev dependencies: {summary['dev_dependencies']}")
    print(f"Internal modules: {summary['internal_modules']}")
    print(f"Coupling score: {summary['coupling_score']}/100 ", end='')

    if summary['coupling_score'] < 30:
        print("(low - good)")
    elif summary['coupling_score'] < 70:
        print("(moderate)")
    else:
        print("(high - consider refactoring)")

    if report['circular_dependencies']:
        print(f"\n--- Circular Dependencies ({len(report['circular_dependencies'])}) ---")
        for cycle in report['circular_dependencies']:
            print(f"  {' -> '.join(cycle)}")

    if report['issues']:
        print(f"\n--- Issues ({len(report['issues'])}) ---")
        for issue in report['issues']:
            severity = issue['severity'].upper()
            print(f"  [{severity}] {issue['message']}")

    if report['recommendations']:
        print(f"\n--- Recommendations ---")
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"  {i}. {rec}")

    # Show top dependencies
    deps = report['dependencies']['direct']
    if deps:
        print(f"\n--- Top Dependencies (of {len(deps)}) ---")
        for name, version in list(deps.items())[:10]:
            print(f"  {name}: {version}")
        if len(deps) > 10:
            print(f"  ... and {len(deps) - 10} more")

    print("\n" + "=" * 60)
