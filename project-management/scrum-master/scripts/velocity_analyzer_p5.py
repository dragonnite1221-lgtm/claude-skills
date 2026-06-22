# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from velocity_analyzer_base import *  # noqa: F403,E402
# fmt: off
from velocity_analyzer_p1 import VelocityAnalysis  # noqa: E402,E501
# fmt: on


def format_text_output(analysis: VelocityAnalysis) -> str:
    """Format analysis results as readable text report."""
    lines = []
    lines.append("="*60)
    lines.append("SPRINT VELOCITY ANALYSIS REPORT")
    lines.append("="*60)
    lines.append("")
    
    if "error" in analysis.summary:
        lines.append(f"ERROR: {analysis.summary['error']}")
        return "\n".join(lines)
    
    # Summary section
    summary = analysis.summary
    lines.append("VELOCITY SUMMARY")
    lines.append("-"*30)
    lines.append(f"Total Sprints Analyzed: {summary['total_sprints']}")
    
    velocity_stats = summary.get("velocity_stats", {})
    lines.append(f"Average Velocity: {velocity_stats.get('mean', 0):.1f} points")
    lines.append(f"Median Velocity: {velocity_stats.get('median', 0):.1f} points")
    lines.append(f"Velocity Range: {velocity_stats.get('min', 0)} - {velocity_stats.get('max', 0)} points")
    lines.append(f"Total Points Completed: {velocity_stats.get('total_points', 0)}")
    lines.append("")
    
    # Volatility analysis
    volatility = summary.get("volatility", {})
    lines.append("VELOCITY STABILITY")
    lines.append("-"*30)
    lines.append(f"Volatility Level: {volatility.get('volatility', 'Unknown').replace('_', ' ').title()}")
    lines.append(f"Coefficient of Variation: {volatility.get('coefficient_of_variation', 0):.2%}")
    lines.append(f"Standard Deviation: {volatility.get('standard_deviation', 0):.1f} points")
    lines.append("")
    
    # Trend analysis
    trend_analysis = analysis.trend_analysis
    lines.append("TREND ANALYSIS")
    lines.append("-"*30)
    lines.append(f"Trend Direction: {trend_analysis.get('trend', 'Unknown').replace('_', ' ').title()}")
    lines.append(f"Trend Confidence: {trend_analysis.get('confidence', 0):.1%}")
    lines.append(f"Velocity Change Rate: {trend_analysis.get('relative_slope', 0):.1%} per sprint")
    lines.append("")
    
    # Forecasting
    forecasting = analysis.forecasting
    lines.append("CAPACITY FORECAST (Next 6 Sprints)")
    lines.append("-"*30)
    if "error" not in forecasting:
        lines.append(f"Expected Total: {forecasting.get('expected_total', 0):.0f} points")
        lines.append(f"Average Per Sprint: {forecasting.get('average_per_sprint', 0):.1f} points")
        
        forecasted_totals = forecasting.get("forecasted_totals", {})
        lines.append("Confidence Intervals:")
        for confidence, total in forecasted_totals.items():
            lines.append(f"  {confidence}: {total:.0f} points")
    else:
        lines.append(f"Forecast unavailable: {forecasting.get('error', 'Unknown error')}")
    lines.append("")
    
    # Anomalies
    if analysis.anomalies:
        lines.append("VELOCITY ANOMALIES")
        lines.append("-"*30)
        for anomaly in analysis.anomalies:
            lines.append(f"Sprint {anomaly['sprint_number']} ({anomaly['sprint_name']})")
            lines.append(f"  Velocity: {anomaly['velocity']} points")
            lines.append(f"  Deviation: {anomaly['deviation_percentage']:.1f}%")
            lines.append(f"  Type: {anomaly['anomaly_type'].replace('_', ' ').title()}")
        lines.append("")
    
    # Recommendations
    if analysis.recommendations:
        lines.append("RECOMMENDATIONS")
        lines.append("-"*30)
        for i, rec in enumerate(analysis.recommendations, 1):
            lines.append(f"{i}. {rec}")
    
    return "\n".join(lines)
def format_json_output(analysis: VelocityAnalysis) -> Dict[str, Any]:
    """Format analysis results as JSON."""
    return {
        "summary": analysis.summary,
        "trend_analysis": analysis.trend_analysis,
        "forecasting": analysis.forecasting,
        "anomalies": analysis.anomalies,
        "recommendations": analysis.recommendations,
    }
