# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from capa_tracker_base import *  # noqa: F403,E402
from capa_tracker_p0 import CAPAMetrics  # noqa: F401,E501


def format_text_output(metrics: CAPAMetrics, aging: Dict) -> str:
    """Format metrics as text report."""
    lines = [
        "=" * 70,
        "CAPA STATUS REPORT",
        "=" * 70,
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "SUMMARY METRICS",
        "-" * 40,
        f"Total CAPAs:        {metrics.total_capas}",
        f"Open CAPAs:         {metrics.open_capas}",
        f"Closed CAPAs:       {metrics.closed_capas}",
        f"Overdue CAPAs:      {metrics.overdue_capas}",
        f"Avg Cycle Time:     {metrics.avg_cycle_time} days",
        f"Effectiveness Rate: {metrics.effectiveness_rate}%",
        "",
        "STATUS DISTRIBUTION",
        "-" * 40,
    ]

    for status, count in metrics.by_status.items():
        bar = "█" * min(count, 20)
        lines.append(f"  {status:<25} {bar} {count}")

    lines.extend([
        "",
        "SEVERITY DISTRIBUTION",
        "-" * 40,
    ])

    for severity, count in metrics.by_severity.items():
        bar = "█" * min(count, 20)
        lines.append(f"  {severity:<25} {bar} {count}")

    lines.extend([
        "",
        "SOURCE DISTRIBUTION",
        "-" * 40,
    ])

    for source, count in metrics.by_source.items():
        bar = "█" * min(count, 20)
        lines.append(f"  {source:<25} {bar} {count}")

    lines.extend([
        "",
        "AGING ANALYSIS",
        "-" * 40,
    ])

    for bucket, capas in aging.items():
        lines.append(f"  {bucket}: {len(capas)} CAPA(s)")

    if metrics.overdue_list:
        lines.extend([
            "",
            "OVERDUE CAPAs",
            "-" * 40,
            f"{'CAPA #':<12} {'Title':<25} {'Days':<6} {'Owner':<15}",
            "-" * 60,
        ])

        for item in metrics.overdue_list[:10]:
            title = item["title"][:24] if len(item["title"]) > 24 else item["title"]
            lines.append(
                f"{item['capa_number']:<12} {title:<25} "
                f"{item['days_overdue']:<6} {item['owner']:<15}"
            )

        if len(metrics.overdue_list) > 10:
            lines.append(f"... and {len(metrics.overdue_list) - 10} more")

    lines.extend([
        "",
        "RECOMMENDATIONS",
        "-" * 40,
    ])

    for i, rec in enumerate(metrics.recommendations, 1):
        lines.append(f"{i}. {rec}")

    lines.append("=" * 70)
    return "\n".join(lines)
