# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from velocity_analyzer_base import *  # noqa: F403,E402
# fmt: off
from velocity_analyzer_p1 import SprintData, VelocityAnalysis, calculate_rolling_averages  # noqa: E402,E501
from velocity_analyzer_p2 import calculate_volatility, detect_trend  # noqa: E402,E501
from velocity_analyzer_p3 import detect_anomalies, monte_carlo_forecast  # noqa: E402,E501
# fmt: on


def generate_recommendations(analysis: VelocityAnalysis) -> List[str]:
    """Generate actionable recommendations based on velocity analysis."""
    recommendations = []
    
    # Trend-based recommendations
    trend = analysis.trend_analysis.get("trend", "")
    if trend == "strong_decline":
        recommendations.append("URGENT: Address strong declining velocity trend. Review impediments, team capacity, and story complexity.")
    elif trend == "decline":
        recommendations.append("Monitor declining velocity. Consider impediment removal and capacity planning review.")
    elif trend == "strong_improvement":
        recommendations.append("Excellent improvement trend! Document successful practices to maintain momentum.")
    
    # Volatility-based recommendations
    volatility = analysis.summary.get("volatility", {}).get("volatility", "")
    if volatility == "very_high":
        recommendations.append("HIGH PRIORITY: Reduce velocity volatility. Review story sizing, definition of done, and sprint planning process.")
    elif volatility == "high":
        recommendations.append("Work on consistency. Review estimation practices and sprint commitment process.")
    elif volatility == "low":
        recommendations.append("Good velocity stability. Continue current practices.")
    
    # Anomaly-based recommendations
    if len(analysis.anomalies) > 0:
        extreme_anomalies = [a for a in analysis.anomalies if a["anomaly_type"] == "extreme_outlier"]
        if extreme_anomalies:
            recommendations.append(f"Investigate {len(extreme_anomalies)} extreme velocity anomalies for root causes.")
    
    # Commitment ratio recommendations
    commitment_ratios = analysis.summary.get("commitment_analysis", {})
    avg_commitment = commitment_ratios.get("average_commitment_ratio", 1.0)
    if avg_commitment < 0.8:
        recommendations.append("Low sprint commitment achievement. Review capacity planning and story complexity estimation.")
    elif avg_commitment > 1.2:
        recommendations.append("Consistently over-committing. Consider more realistic sprint planning.")
    
    return recommendations
def analyze_velocity(data: Dict[str, Any]) -> VelocityAnalysis:
    """Perform comprehensive velocity analysis."""
    analysis = VelocityAnalysis()
    
    try:
        # Parse sprint data
        sprint_records = data.get("sprints", [])
        sprints = [SprintData(record) for record in sprint_records]
        
        if not sprints:
            raise ValueError("No sprint data found")
        
        # Sort by sprint number
        sprints.sort(key=lambda s: s.sprint_number)
        
        # Basic summary statistics
        velocities = [sprint.velocity for sprint in sprints]
        commitment_ratios = [sprint.commitment_ratio for sprint in sprints]
        scope_change_ratios = [sprint.scope_change_ratio for sprint in sprints]
        
        analysis.summary = {
            "total_sprints": len(sprints),
            "velocity_stats": {
                "mean": statistics.mean(velocities),
                "median": statistics.median(velocities),
                "min": min(velocities),
                "max": max(velocities),
                "total_points": sum(velocities),
            },
            "commitment_analysis": {
                "average_commitment_ratio": statistics.mean(commitment_ratios),
                "commitment_consistency": statistics.stdev(commitment_ratios) if len(commitment_ratios) > 1 else 0,
                "sprints_under_committed": sum(1 for r in commitment_ratios if r < 1.0),
                "sprints_over_committed": sum(1 for r in commitment_ratios if r > 1.0),
            },
            "scope_change_analysis": {
                "average_scope_change": statistics.mean(scope_change_ratios),
                "scope_change_volatility": statistics.stdev(scope_change_ratios) if len(scope_change_ratios) > 1 else 0,
            },
            "rolling_averages": calculate_rolling_averages(sprints),
            "volatility": calculate_volatility(sprints),
        }
        
        # Trend analysis
        analysis.trend_analysis = detect_trend(sprints)
        
        # Forecasting
        analysis.forecasting = monte_carlo_forecast(sprints, sprints_ahead=6)
        
        # Anomaly detection
        analysis.anomalies = detect_anomalies(sprints)
        
        # Generate recommendations
        analysis.recommendations = generate_recommendations(analysis)
        
    except Exception as e:
        analysis.summary = {"error": str(e)}
    
    return analysis
