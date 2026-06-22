# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from fmea_analyzer_base import *  # noqa: F403,E402
# fmt: off
from fmea_analyzer_p1 import FMEAReport  # noqa: E402,E501
# fmt: on


def format_fmea_text(report: FMEAReport) -> str:
    """Format FMEA report as text."""
    lines = [
        "=" * 80,
        f"{report.fmea_type.upper()} REPORT",
        "=" * 80,
        f"Product/Process: {report.product_process}",
        f"Date: {report.date}",
        f"Team: {', '.join(report.team)}",
        "",
        "SUMMARY",
        "-" * 60,
        f"Total Failure Modes Analyzed: {report.summary['total_entries']}",
        f"Critical Severity (≥8): {report.summary['risk_distribution']['critical_severity']}",
        f"High RPN (≥100): {report.summary['risk_distribution']['high_rpn']}",
        f"Medium RPN (50-99): {report.summary['risk_distribution']['medium_rpn']}",
        "",
        "RPN Statistics:",
        f"  Min: {report.summary['rpn_statistics']['min']}",
        f"  Max: {report.summary['rpn_statistics']['max']}",
        f"  Average: {report.summary['rpn_statistics']['average']}",
        f"  Median: {report.summary['rpn_statistics']['median']}",
    ]

    if "revised_rpn_statistics" in report.summary:
        lines.extend([
            "",
            "Revised RPN Statistics:",
            f"  Average: {report.summary['revised_rpn_statistics']['average']}",
            f"  Improvement: {report.summary['revised_rpn_statistics']['improvement']}%",
        ])

    lines.extend([
        "",
        "TOP RISKS",
        "-" * 60,
        f"{'Item':<25} {'Failure Mode':<30} {'RPN':>5} {'Sev':>4}",
        "-" * 66,
    ])
    for risk in report.summary.get("top_risks", []):
        lines.append(f"{risk['item'][:24]:<25} {risk['failure_mode'][:29]:<30} {risk['rpn']:>5} {risk['severity']:>4}")

    lines.extend([
        "",
        "FMEA ENTRIES",
        "-" * 60,
    ])

    for i, entry in enumerate(report.entries, 1):
        marker = "⚠" if entry.criticality in ["CRITICAL", "HIGH"] else "•"
        lines.extend([
            f"",
            f"{marker} Entry {i}: {entry.item_process} - {entry.function}",
            f"  Failure Mode: {entry.failure_mode}",
            f"  Effect: {entry.effect}",
            f"  Cause: {entry.cause}",
            f"  S={entry.severity} × O={entry.occurrence} × D={entry.detection} = RPN {entry.rpn} [{entry.criticality}]",
            f"  Current Controls: {entry.current_controls}",
        ])
        if entry.recommended_actions:
            lines.append(f"  Recommended Actions:")
            for action in entry.recommended_actions:
                lines.append(f"    → {action}")
        if entry.revised_rpn > 0:
            lines.append(f"  Revised: S={entry.revised_severity} × O={entry.revised_occurrence} × D={entry.revised_detection} = RPN {entry.revised_rpn}")

    if report.risk_reduction_actions:
        lines.extend([
            "",
            "RISK REDUCTION RECOMMENDATIONS",
            "-" * 60,
        ])
        for action in report.risk_reduction_actions:
            lines.extend([
                f"",
                f"  {action['item']} - {action['failure_mode']}",
                f"  Current RPN: {action['current_rpn']} (Severity: {action['current_severity']})",
            ])
            for strategy in action["strategies"]:
                lines.append(f"    [{strategy['priority']}] {strategy['type']}: {strategy['action']}")
                lines.append(f"      Expected: {strategy['expected_impact']}")

    lines.append("=" * 80)
    return "\n".join(lines)
