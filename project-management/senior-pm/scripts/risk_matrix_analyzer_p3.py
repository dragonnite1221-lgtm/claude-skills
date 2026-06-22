# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from risk_matrix_analyzer_base import *  # noqa: F403,E402
# fmt: off
from risk_matrix_analyzer_p1 import RISK_CATEGORIES  # noqa: E402,E501
from risk_matrix_analyzer_p2 import Risk, _classify_risk_exposure  # noqa: E402,E501
# fmt: on


def build_risk_matrix(risks: List[Risk]) -> Dict[str, Any]:
    """Build probability/impact risk matrix with risk distribution."""
    matrix = {}
    risk_distribution = {}
    
    # Initialize matrix
    for prob in range(1, 6):
        matrix[prob] = {}
        for impact in range(1, 6):
            matrix[prob][impact] = []
    
    # Populate matrix with risks
    for risk in risks:
        if risk.is_active:
            matrix[risk.probability][risk.impact].append({
                "id": risk.id,
                "title": risk.title,
                "risk_score": risk.risk_score,
                "category": risk.category
            })
    
    # Calculate distribution statistics
    total_risks = len([r for r in risks if r.is_active])
    risk_distribution = {
        "critical": len([r for r in risks if r.is_active and r.risk_level == "critical"]),
        "high": len([r for r in risks if r.is_active and r.risk_level == "high"]),
        "medium": len([r for r in risks if r.is_active and r.risk_level == "medium"]),
        "low": len([r for r in risks if r.is_active and r.risk_level == "low"])
    }
    
    # Calculate risk exposure
    total_score = sum(r.risk_score for r in risks if r.is_active)
    average_score = total_score / max(total_risks, 1)
    
    return {
        "matrix": matrix,
        "distribution": risk_distribution,
        "total_risks": total_risks,
        "total_risk_score": total_score,
        "average_risk_score": average_score,
        "risk_exposure_level": _classify_risk_exposure(average_score)
    }
def _get_risk_level_distribution(risks: List[Risk]) -> Dict[str, int]:
    """Get distribution of risk levels for a set of risks."""
    distribution = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for risk in risks:
        distribution[risk.risk_level] += 1
    return distribution
def _calculate_mitigation_coverage(risks: List[Risk]) -> float:
    """Calculate percentage of risks with defined mitigation actions."""
    if not risks:
        return 0.0
    
    risks_with_mitigation = sum(1 for r in risks if r.mitigation_actions)
    return risks_with_mitigation / len(risks)
def analyze_risk_categories(risks: List[Risk]) -> Dict[str, Any]:
    """Analyze risks by category with detailed statistics."""
    category_stats = {}
    active_risks = [r for r in risks if r.is_active]
    
    for category, config in RISK_CATEGORIES.items():
        category_risks = [r for r in active_risks if r.category == category]
        
        if category_risks:
            risk_scores = [r.risk_score for r in category_risks]
            category_stats[category] = {
                "count": len(category_risks),
                "total_score": sum(risk_scores),
                "average_score": statistics.mean(risk_scores),
                "max_score": max(risk_scores),
                "risk_level_distribution": _get_risk_level_distribution(category_risks),
                "top_risks": sorted(category_risks, key=lambda r: r.risk_score, reverse=True)[:3],
                "mitigation_coverage": _calculate_mitigation_coverage(category_risks),
                "suggested_strategies": config["mitigation_strategies"][:3]
            }
        else:
            category_stats[category] = {
                "count": 0,
                "total_score": 0,
                "average_score": 0,
                "risk_level_distribution": {},
                "mitigation_coverage": 0
            }
    
    # Identify highest risk categories
    sorted_categories = sorted(
        [(cat, stats) for cat, stats in category_stats.items() if stats["count"] > 0],
        key=lambda x: x[1]["total_score"],
        reverse=True
    )
    
    return {
        "category_statistics": category_stats,
        "highest_risk_categories": [cat for cat, _ in sorted_categories[:3]],
        "category_concentration": len([c for c in category_stats if category_stats[c]["count"] > 0])
    }
