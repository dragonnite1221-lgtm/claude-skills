# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from debt_dashboard_base import *  # noqa: F403,E402


@dataclass
class HealthMetrics:
    """Health metrics for a specific time period."""
    overall_score: float  # 0-100
    debt_density: float  # debt items per file
    velocity_impact: float  # estimated velocity reduction %
    quality_score: float  # 0-100
    maintainability_score: float  # 0-100
    technical_risk_score: float  # 0-100


@dataclass
class TrendAnalysis:
    """Trend analysis for debt metrics over time."""
    metric_name: str
    trend_direction: str  # "improving", "declining", "stable"
    change_rate: float  # rate of change per period
    correlation_strength: float  # -1 to 1
    forecast_next_period: float
    confidence_interval: Tuple[float, float]


@dataclass
class DebtVelocity:
    """Debt velocity tracking - how fast debt is being created vs resolved."""
    period: str
    new_debt_items: int
    resolved_debt_items: int
    net_change: int
    velocity_ratio: float  # resolved/new, >1 is good
    effort_hours_added: float
    effort_hours_resolved: float
    net_effort_change: float


def format_dashboard_report(dashboard_data: Dict[str, Any]) -> str:
    """Format dashboard data into human-readable report."""
    output = []
    
    # Header
    output.append("=" * 60)
    output.append("TECHNICAL DEBT DASHBOARD")
    output.append("=" * 60)
    metadata = dashboard_data["metadata"]
    output.append(f"Generated: {metadata['generated_date'][:19]}")
    output.append(f"Analysis Period: {metadata['analysis_period']}")
    output.append(f"Snapshots Analyzed: {metadata['snapshots_analyzed']}")
    if metadata["date_range"]["start"]:
        output.append(f"Date Range: {metadata['date_range']['start'][:10]} to {metadata['date_range']['end'][:10]}")
    output.append("")
    
    # Executive Summary
    exec_summary = dashboard_data["executive_summary"]
    output.append("EXECUTIVE SUMMARY")
    output.append("-" * 30)
    output.append(f"Overall Status: {exec_summary['overall_status'].upper()}")
    output.append(f"Health Score: {exec_summary['health_score']:.1f}/100")
    output.append(f"Status: {exec_summary['status_message']}")
    output.append("")
    output.append("Key Metrics:")
    output.append(f"  • Total Debt Items: {exec_summary['total_debt_items']}")
    output.append(f"  • High Priority Items: {exec_summary['high_priority_items']}")
    output.append(f"  • Estimated Effort: {exec_summary['estimated_effort_hours']:.1f} hours")
    output.append(f"  • Velocity Impact: {exec_summary['velocity_impact_percent']:.1f}%")
    output.append("")
    
    if exec_summary["key_insights"]:
        output.append("Key Insights:")
        for insight in exec_summary["key_insights"]:
            output.append(f"  • {insight}")
        output.append("")
    
    # Current Health
    if dashboard_data["current_health"]:
        health = dashboard_data["current_health"]
        output.append("CURRENT HEALTH METRICS")
        output.append("-" * 30)
        output.append(f"Overall Score: {health['overall_score']:.1f}/100")
        output.append(f"Quality Score: {health['quality_score']:.1f}/100")
        output.append(f"Maintainability: {health['maintainability_score']:.1f}/100")
        output.append(f"Technical Risk: {health['technical_risk_score']:.1f}/100")
        output.append(f"Debt Density: {health['debt_density']:.2f} items/file")
        output.append("")
    
    # Trend Analysis
    trends = dashboard_data["trend_analysis"]
    if trends:
        output.append("TREND ANALYSIS")
        output.append("-" * 30)
        for metric, trend in trends.items():
            direction_symbol = {
                "improving": "↑",
                "declining": "↓", 
                "stable": "→"
            }.get(trend["trend_direction"], "→")
            
            output.append(f"{metric.replace('_', ' ').title()}: {direction_symbol} {trend['trend_direction']}")
            output.append(f"  Change Rate: {trend['change_rate']:.3f} per period")
            output.append(f"  Forecast: {trend['forecast_next_period']:.1f}")
        output.append("")
    
    # Top Recommendations
    recommendations = dashboard_data["recommendations"]
    if recommendations:
        output.append("TOP RECOMMENDATIONS")
        output.append("-" * 30)
        for i, rec in enumerate(recommendations[:5], 1):
            output.append(f"{i}. [{rec['priority'].upper()}] {rec['title']}")
            output.append(f"   {rec['description']}")
            output.append(f"   Impact: {rec['impact']}, Effort: {rec['effort']}")
            output.append("")
    
    return "\n".join(output)
