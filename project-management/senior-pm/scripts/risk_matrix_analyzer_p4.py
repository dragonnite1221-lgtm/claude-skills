# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from risk_matrix_analyzer_base import *  # noqa: F403,E402
# fmt: off
from risk_matrix_analyzer_p1 import MITIGATION_STRATEGIES  # noqa: E402,E501
from risk_matrix_analyzer_p2 import Risk  # noqa: E402,E501
from risk_matrix_analyzer_p3 import _get_risk_level_distribution  # noqa: E402,E501
# fmt: on


def analyze_mitigation_effectiveness(risks: List[Risk]) -> Dict[str, Any]:
    """Analyze mitigation strategy effectiveness and coverage."""
    active_risks = [r for r in risks if r.is_active]
    
    # Mitigation strategy distribution
    strategy_distribution = {}
    for strategy in MITIGATION_STRATEGIES.keys():
        strategy_risks = [r for r in active_risks if r.mitigation_strategy == strategy]
        if strategy_risks:
            strategy_distribution[strategy] = {
                "count": len(strategy_risks),
                "average_risk_score": statistics.mean([r.risk_score for r in strategy_risks]),
                "risk_levels": _get_risk_level_distribution(strategy_risks)
            }
    
    # Mitigation coverage analysis
    risks_with_mitigation = [r for r in active_risks if r.mitigation_actions]
    mitigation_coverage = len(risks_with_mitigation) / max(len(active_risks), 1)
    
    # Action item analysis
    total_actions = sum(len(r.mitigation_actions) for r in active_risks)
    average_actions_per_risk = total_actions / max(len(active_risks), 1)
    
    # Overdue mitigation analysis
    overdue_risks = [r for r in active_risks if r.is_overdue]
    overdue_rate = len(overdue_risks) / max(len(active_risks), 1)
    
    return {
        "strategy_distribution": strategy_distribution,
        "mitigation_coverage": mitigation_coverage,
        "average_actions_per_risk": average_actions_per_risk,
        "overdue_mitigation_count": len(overdue_risks),
        "overdue_rate": overdue_rate,
        "top_overdue_risks": sorted(overdue_risks, key=lambda r: r.risk_score, reverse=True)[:5]
    }
def analyze_risk_trends(current_risks: List[Risk], historical_data: Optional[List[Dict]] = None) -> Dict[str, Any]:
    """Analyze risk trends over time if historical data is available."""
    if not historical_data:
        return {
            "trend_analysis_available": False,
            "message": "Historical data required for trend analysis"
        }
    
    # Simple trend analysis based on current vs. historical risk levels
    current_total_score = sum(r.risk_score for r in current_risks if r.is_active)
    current_risk_count = len([r for r in current_risks if r.is_active])
    
    # This is a simplified implementation - in practice, you'd track risks over time
    trend_data = {
        "trend_analysis_available": True,
        "current_total_risk_score": current_total_score,
        "current_active_risks": current_risk_count,
        "risk_velocity": {
            "new_risks_rate": "Calculate from historical data",
            "resolution_rate": "Calculate from historical data",
            "escalation_rate": "Calculate from historical data"
        }
    }
    
    return trend_data
def generate_risk_recommendations(risks: List[Risk], analysis_results: Dict[str, Any]) -> List[str]:
    """Generate actionable risk management recommendations."""
    recommendations = []
    
    # Critical risk recommendations
    critical_risks = [r for r in risks if r.is_active and r.risk_level == "critical"]
    if critical_risks:
        recommendations.append(f"URGENT: Address {len(critical_risks)} critical risks immediately. These require executive attention and dedicated resources.")
        
        for risk in critical_risks[:3]:  # Top 3 critical risks
            recommendations.append(f"Critical Risk - {risk.title}: Implement {risk.suggested_approach} strategy within 48 hours.")
    
    # High-concentration category recommendations
    category_analysis = analysis_results.get("category_analysis", {})
    highest_categories = category_analysis.get("highest_risk_categories", [])
    
    if highest_categories:
        top_category = highest_categories[0]
        recommendations.append(f"Focus mitigation efforts on {top_category} risks - highest concentration of risk exposure.")
    
    # Mitigation coverage recommendations
    mitigation_analysis = analysis_results.get("mitigation_analysis", {})
    coverage = mitigation_analysis.get("mitigation_coverage", 0)
    
    if coverage < 0.7:
        recommendations.append("Improve mitigation coverage - less than 70% of risks have defined mitigation actions.")
    
    overdue_rate = mitigation_analysis.get("overdue_rate", 0)
    if overdue_rate > 0.2:
        recommendations.append("Address overdue mitigation actions - more than 20% of risks are past their target resolution date.")
    
    # Risk matrix recommendations
    matrix_analysis = analysis_results.get("risk_matrix", {})
    avg_score = matrix_analysis.get("average_risk_score", 0)
    
    if avg_score > 15:
        recommendations.append("Portfolio risk exposure is high. Consider scope reduction or additional risk mitigation investments.")
    elif avg_score < 8:
        recommendations.append("Risk exposure is well-managed. Consider taking on additional strategic initiatives.")
    
    return recommendations
