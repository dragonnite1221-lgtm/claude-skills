# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from management_review_tracker_base import *  # noqa: F403,E402


def format_text_report(report: Dict) -> str:
    """Format report as text output."""
    lines = [
        "=" * 70,
        "MANAGEMENT REVIEW STATUS REPORT",
        "=" * 70,
        f"Review Date: {report['review_date']}",
        f"Review Type: {report['review_type']}",
        f"Period: {report['period']}",
        "",
        "INPUT READINESS",
        "-" * 40,
        f"Readiness Score: {report['input_readiness']['readiness_score']}%",
        f"Complete: {report['input_readiness']['complete']} / {report['input_readiness']['total_required']}",
    ]

    if report['input_readiness']['missing_topics']:
        lines.append(f"Missing: {', '.join(report['input_readiness']['missing_topics'])}")

    lines.extend([
        "",
        "ACTION STATUS",
        "-" * 40,
        f"Total Actions: {report['action_analysis']['total']}",
        f"Completion Rate: {report['action_analysis']['completion_rate']}%",
    ])

    for status, count in report['action_analysis']['by_status'].items():
        lines.append(f"  {status}: {count}")

    if report['action_analysis']['overdue']:
        lines.extend([
            "",
            "OVERDUE ACTIONS:",
        ])
        for item in report['action_analysis']['overdue']:
            lines.append(f"  [{item['action_id']}] {item['description']} - {item['days_overdue']} days overdue")

    lines.extend([
        "",
        "METRICS ASSESSMENT",
        "-" * 40,
        f"Overall Status: {report['metrics_assessment']['overall_status']}",
        "",
        f"{'Metric':<25} {'Value':<10} {'Target':<10} {'Status':<10}",
        "-" * 55,
    ])

    for metric in report['metrics_assessment']['metrics']:
        lines.append(
            f"{metric['name']:<25} {metric['value']:<10} {metric['target']:<10} {metric['status']:<10}"
        )

    if report['metrics_assessment']['alerts']:
        lines.extend([
            "",
            "ALERTS:",
        ])
        for alert in report['metrics_assessment']['alerts']:
            lines.append(f"  ! {alert}")

    lines.extend([
        "",
        "RECOMMENDATIONS",
        "-" * 40,
    ])

    for i, rec in enumerate(report['recommendations'], 1):
        lines.append(f"{i}. {rec}")

    lines.append("=" * 70)
    return "\n".join(lines)
