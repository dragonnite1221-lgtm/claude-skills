# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from project_architect_base import *  # noqa: F403,E402


def print_human_report(report: Dict):
    """Print human-readable report."""
    print("\n" + "=" * 60)
    print("ARCHITECTURE ASSESSMENT")
    print("=" * 60)
    print(f"\nProject: {report['project_path']}")

    arch = report['architecture']
    print(f"\n--- Architecture Pattern ---")
    print(f"Detected: {arch['detected_pattern'].replace('_', ' ').title()}")
    print(f"Confidence: {arch['confidence']}%")

    if arch['layer_assignments']:
        print(f"\nLayer Assignments:")
        for dir_name, layer in sorted(arch['layer_assignments'].items()):
            if layer != 'unknown':
                status = "OK"
            else:
                status = "?"
            print(f"  {status} {dir_name:20} -> {layer}")

    summary = report['summary']
    print(f"\n--- Summary ---")
    print(f"Total issues: {summary['total_issues']}")
    print(f"  Code issues: {summary['code_issues']}")
    print(f"  Layer violations: {summary['layer_violations']}")

    if report['code_quality']['issues']:
        print(f"\n--- Code Issues ---")
        for issue in report['code_quality']['issues'][:10]:
            severity = issue['severity'].upper()
            print(f"  [{severity}] {issue.get('file', 'N/A')}")
            print(f"          {issue['message']}")
            if 'suggestion' in issue:
                print(f"          Suggestion: {issue['suggestion']}")

    if report['layer_violations']:
        print(f"\n--- Layer Violations ---")
        for v in report['layer_violations'][:5]:
            print(f"  {v['file']}")
            print(f"      {v['message']}")

    if report['recommendations']:
        print(f"\n--- Recommendations ---")
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"  {i}. {rec}")

    metrics = report['code_quality']['metrics']
    print(f"\n--- Metrics ---")
    print(f"  Total lines: {metrics.get('total_lines', 'N/A')}")
    print(f"  File count: {metrics.get('file_count', 'N/A')}")
    print(f"  Avg lines/file: {metrics.get('avg_file_lines', 'N/A')}")

    print("\n" + "=" * 60)
