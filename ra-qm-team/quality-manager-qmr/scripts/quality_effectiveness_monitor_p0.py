# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from quality_effectiveness_monitor_base import *  # noqa: F403,E402


@dataclass
class QualityMetric:
    """A single quality metric data point."""
    metric_id: str
    metric_name: str
    category: str
    date: str
    value: float
    unit: str
    target: float
    upper_limit: float
    lower_limit: float
    trend_direction: str = ""  # "up", "down", "stable"
    sigma_level: float = 0.0
    is_alert: bool = False
    is_critical: bool = False


@dataclass
class QMSReport:
    """QMS effectiveness report."""
    report_period: Tuple[str, str]
    overall_effectiveness_score: float
    metrics_count: int
    metrics_in_control: int
    metrics_out_of_control: int
    critical_alerts: int
    trends_analysis: Dict
    predictive_alerts: List[Dict]
    improvement_opportunities: List[Dict]
    management_review_summary: str


def format_qms_report(report: QMSReport) -> str:
    """Format QMS report as text."""
    lines = [
        "=" * 80,
        "QMS EFFECTIVENESS MONITORING REPORT",
        "=" * 80,
        f"Period: {report.report_period[0]} to {report.report_period[1]}",
        f"Overall Score: {report.overall_effectiveness_score:.1f}/100",
        "",
        "METRIC STATUS",
        "-" * 40,
        f"  Total Metrics: {report.metrics_count}",
        f"  In Control: {report.metrics_in_control}",
        f"  Out of Control: {report.metrics_out_of_control}",
        f"  Critical Alerts: {report.critical_alerts}",
        "",
        "TREND ANALYSIS BY CATEGORY",
        "-" * 40,
    ]

    for category, data in report.trends_analysis.items():
        lines.append(f"  {category}: {data['avg_value']} (alerts: {data['alerts']})")

    if report.predictive_alerts:
        lines.extend([
            "",
            "PREDICTIVE ALERTS (Next 30 days)",
            "-" * 40,
        ])
        for alert in report.predictive_alerts[:5]:
            lines.append(f"  ⚠ {alert['metric']}: {alert['current_value']} → {alert['forecast_value']} ({alert['risk_level']})")

    if report.improvement_opportunities:
        lines.extend([
            "",
            "TOP IMPROVEMENT OPPORTUNITIES",
            "-" * 40,
        ])
        for i, opp in enumerate(report.improvement_opportunities[:5], 1):
            lines.append(f"  {i}. {opp['metric']}: {opp['recommended_action']}")

    lines.extend([
        "",
        "MANAGEMENT REVIEW SUMMARY",
        "-" * 40,
        report.management_review_summary,
        "=" * 80
    ])

    return "\n".join(lines)
