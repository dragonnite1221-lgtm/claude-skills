# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from code_quality_analyzer_base import *  # noqa: F403,E402


def print_report(analysis: Dict, verbose: bool = False) -> None:
    """Print human-readable report."""
    print("=" * 60)
    print("CODE QUALITY ANALYSIS REPORT")
    print("=" * 60)
    print()

    # Summary
    summary = analysis["summary"]
    print(f"Overall Score: {analysis['overall_score']}/100 (Grade: {analysis['grade']})")
    print(f"Files Analyzed: {summary['files_analyzed']}")
    print(f"Total Lines: {summary['total_lines']:,}")
    print(f"Code Lines: {summary['code_lines']:,}")
    print(f"Comment Lines: {summary['comment_lines']:,}")
    print()

    # Languages
    print("--- LANGUAGES ---")
    for lang, stats in analysis["languages"].items():
        print(f"  {lang}: {stats['files']} files, {stats['lines']:,} lines")
    print()

    # Security
    sec = analysis["security"]
    total_sec = sum(len(sec[s]) for s in ["critical", "high", "medium", "low"])
    print("--- SECURITY ---")
    print(f"  Critical: {len(sec['critical'])}")
    print(f"  High: {len(sec['high'])}")
    print(f"  Medium: {len(sec['medium'])}")
    print(f"  Low: {len(sec['low'])}")
    if total_sec > 0 and verbose:
        print("  Issues:")
        for severity in ["critical", "high", "medium"]:
            for issue in sec[severity][:3]:
                print(f"    [{severity.upper()}] {issue['file']}:{issue['line']} - {issue['message']}")
    print()

    # Complexity
    cplx = analysis["complexity"]
    print("--- COMPLEXITY ---")
    print(f"  Average Complexity: {cplx['average_complexity']}")
    print(f"  High Complexity Files: {len(cplx['high_complexity_files'])}")
    print()

    # Dependencies
    deps = analysis["dependencies"]
    print("--- DEPENDENCIES ---")
    print(f"  Package Managers: {', '.join(deps.get('package_managers', ['none']))}")
    print(f"  Total Dependencies: {deps.get('total_deps', 0)}")
    print(f"  Vulnerable: {len(deps.get('vulnerable', []))}")
    print()

    # Tests
    tests = analysis["tests"]
    print("--- TEST COVERAGE ---")
    print(f"  Source Files: {tests.get('source_files', 0)}")
    print(f"  Test Files: {tests.get('test_files', 0)}")
    print(f"  Estimated Coverage: {tests.get('estimated_coverage', 0)}% ({tests.get('rating', 'unknown')})")
    print()

    # Documentation
    docs = analysis["documentation"]
    print("--- DOCUMENTATION ---")
    print(f"  README: {'Yes' if docs.get('has_readme') else 'No'}")
    print(f"  LICENSE: {'Yes' if docs.get('has_license') else 'No'}")
    print(f"  CONTRIBUTING: {'Yes' if docs.get('has_contributing') else 'No'}")
    print(f"  CHANGELOG: {'Yes' if docs.get('has_changelog') else 'No'}")
    print(f"  Score: {docs.get('score', 0)}/100")
    print()

    # Recommendations
    if analysis["recommendations"]:
        print("--- RECOMMENDATIONS ---")
        for i, rec in enumerate(analysis["recommendations"][:10], 1):
            print(f"\n{i}. [{rec['priority']}] {rec['category'].upper()}")
            print(f"   Issue: {rec['issue']}")
            print(f"   Action: {rec['action']}")

    print()
    print("=" * 60)
