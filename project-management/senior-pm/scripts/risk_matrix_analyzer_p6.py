# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from risk_matrix_analyzer_base import *  # noqa: F403,E402
# fmt: off
from risk_matrix_analyzer_p2 import RiskAnalysisResult  # noqa: E402,E501
# fmt: on


def format_text_output(result: RiskAnalysisResult) -> str:
    """Format analysis results as readable text report."""
    lines = []
    lines.append("="*60)
    lines.append("RISK MATRIX ANALYSIS REPORT")
    lines.append("="*60)
    lines.append("")
    
    if "error" in result.summary:
        lines.append(f"ERROR: {result.summary['error']}")
        return "\n".join(lines)
    
    # Executive Summary
    summary = result.summary
    lines.append("EXECUTIVE SUMMARY")
    lines.append("-"*30)
    lines.append(f"Total Risks: {summary['total_risks']} ({summary['active_risks']} active)")
    lines.append(f"Risk Exposure: {summary['total_risk_exposure']:.1f} points (avg: {summary['average_risk_score']:.1f})")
    lines.append(f"Critical/High Risks: {summary['critical_risks']}/{summary['high_risks']}")
    lines.append(f"Overdue Mitigations: {summary['overdue_risks']}")
    lines.append("")
    
    # Risk Distribution
    matrix = result.risk_matrix
    lines.append("RISK LEVEL DISTRIBUTION")
    lines.append("-"*30)
    distribution = matrix.get("distribution", {})
    for level in ["critical", "high", "medium", "low"]:
        count = distribution.get(level, 0)
        percentage = (count / max(summary["active_risks"], 1)) * 100
        lines.append(f"{level.title()}: {count} ({percentage:.1f}%)")
    lines.append("")
    
    # Risk Matrix Visualization
    lines.append("RISK MATRIX (Probability vs Impact)")
    lines.append("-"*50)
    lines.append("     1    2    3    4    5   (Impact)")
    
    matrix_data = matrix.get("matrix", {})
    for prob in range(5, 0, -1):
        line = f"{prob} "
        for impact in range(1, 6):
            risk_count = len(matrix_data.get(prob, {}).get(impact, []))
            line += f" [{risk_count:2}]"
        lines.append(line)
    lines.append("(P)")
    lines.append("")
    
    # Category Analysis
    category_analysis = result.category_analysis
    lines.append("RISK BY CATEGORY")
    lines.append("-"*30)
    
    category_stats = category_analysis.get("category_statistics", {})
    for category, stats in category_stats.items():
        if stats["count"] > 0:
            lines.append(f"{category.title()}: {stats['count']} risks, "
                        f"avg score: {stats['average_score']:.1f}, "
                        f"total exposure: {stats['total_score']:.1f}")
    lines.append("")
    
    # Mitigation Analysis
    mitigation = result.mitigation_analysis
    lines.append("MITIGATION EFFECTIVENESS")
    lines.append("-"*30)
    lines.append(f"Mitigation Coverage: {mitigation.get('mitigation_coverage', 0):.1%}")
    lines.append(f"Average Actions per Risk: {mitigation.get('average_actions_per_risk', 0):.1f}")
    lines.append(f"Overdue Mitigations: {mitigation.get('overdue_mitigation_count', 0)} "
                f"({mitigation.get('overdue_rate', 0):.1%})")
    lines.append("")
    
    # Top Risks
    lines.append("TOP RISKS REQUIRING ATTENTION")
    lines.append("-"*30)
    
    # Find top risks across all categories
    all_risks = []
    for category_stats in category_stats.values():
        if "top_risks" in category_stats:
            all_risks.extend(category_stats["top_risks"])
    
    top_risks = sorted(all_risks, key=lambda r: r.risk_score, reverse=True)[:5]
    for i, risk in enumerate(top_risks, 1):
        lines.append(f"{i}. {risk.title} (Score: {risk.risk_score:.1f}, Level: {risk.risk_level.title()})")
        lines.append(f"   Category: {risk.category.title()}, Strategy: {risk.suggested_approach.title()}")
    lines.append("")
    
    # Recommendations
    if result.recommendations:
        lines.append("RECOMMENDATIONS")
        lines.append("-"*30)
        for i, rec in enumerate(result.recommendations, 1):
            lines.append(f"{i}. {rec}")
    
    return "\n".join(lines)
def format_json_output(result: RiskAnalysisResult) -> Dict[str, Any]:
    """Format analysis results as JSON."""
    # Convert Risk objects to dictionaries for JSON serialization
    def serialize_risks(obj):
        if isinstance(obj, list):
            return [serialize_risks(item) for item in obj]
        elif hasattr(obj, 'id') and hasattr(obj, 'title'):  # This is a Risk object
            return {
                "id": obj.id,
                "title": obj.title,
                "risk_score": obj.risk_score,
                "risk_level": obj.risk_level,
                "category": obj.category,
                "probability": obj.probability,
                "impact": obj.impact,
                "status": obj.status
            }
        elif isinstance(obj, dict):
            return {key: serialize_risks(value) for key, value in obj.items()}
        else:
            return obj
    
    # Deep copy and serialize all risk objects recursively
    return serialize_risks({
        "summary": result.summary,
        "risk_matrix": result.risk_matrix,
        "category_analysis": result.category_analysis,
        "mitigation_analysis": result.mitigation_analysis,
        "trend_analysis": result.trend_analysis,
        "recommendations": result.recommendations
    })
