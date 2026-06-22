# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from retrospective_analyzer_base import *  # noqa: F403,E402
# fmt: off
from retrospective_analyzer_p2 import RetroAnalysisResult, RetrospectiveData  # noqa: E402,E501
from retrospective_analyzer_p3 import analyze_action_item_completion  # noqa: E402,E501
from retrospective_analyzer_p4 import analyze_recurring_themes  # noqa: E402,E501
from retrospective_analyzer_p6 import analyze_improvement_trends  # noqa: E402,E501
# fmt: on


def generate_recommendations(result: RetroAnalysisResult) -> List[str]:
    """Generate actionable recommendations based on retrospective analysis."""
    recommendations = []
    
    # Action item recommendations
    action_analysis = result.action_item_analysis
    completion_rate = action_analysis.get("completion_rate", 0)
    
    if completion_rate < 0.5:
        recommendations.append("CRITICAL: Low action item completion rate (<50%). Reduce action items per retro and focus on realistic, achievable goals.")
    elif completion_rate < 0.7:
        recommendations.append("Improve action item follow-through. Consider assigning owners and due dates more systematically.")
    elif completion_rate > 0.9:
        recommendations.append("Excellent action item completion! Consider taking on more ambitious improvement initiatives.")
    
    overdue_rate = action_analysis.get("overdue_rate", 0)
    if overdue_rate > 0.3:
        recommendations.append("High overdue rate suggests unrealistic timelines. Review estimation and prioritization process.")
    
    # Theme recommendations
    theme_analysis = result.theme_analysis
    persistent_issues = theme_analysis.get("persistent_issues", [])
    if len(persistent_issues) >= 2:
        recommendations.append(f"Address {len(persistent_issues)} persistent issues that keep recurring across retrospectives.")
        for issue in persistent_issues[:2]:  # Top 2 issues
            recommendations.append(f"Focus on resolving recurring {issue['theme']} issues (appears in {issue['frequency']:.0%} of retros).")
    
    # Trend-based recommendations
    improvement_trends = result.improvement_trends
    if "team_maturity_score" in improvement_trends:
        maturity = improvement_trends["team_maturity_score"]
        level = maturity.get("level", "forming")
        
        if level == "forming":
            recommendations.append("Team is in forming stage. Focus on establishing basic retrospective disciplines and psychological safety.")
        elif level == "developing":
            recommendations.append("Team is developing. Work on action item follow-through and deeper root cause analysis.")
        elif level == "performing":
            recommendations.append("Good team maturity. Consider advanced techniques like continuous improvement tracking.")
        elif level == "high_performing":
            recommendations.append("Excellent retrospective maturity! Share practices with other teams and focus on innovation.")
    
    # Quality recommendations
    if "retrospective_quality_trend" in improvement_trends:
        quality_trend = improvement_trends["retrospective_quality_trend"]
        avg_quality = quality_trend.get("average_quality", 50)
        
        if avg_quality < 60:
            recommendations.append("Retrospective quality is below average. Review facilitation techniques and engagement strategies.")
        
        trend_direction = quality_trend.get("trend", {}).get("direction", "stable")
        if trend_direction == "decreasing":
            recommendations.append("Retrospective quality is declining. Consider changing facilitation approach or addressing team engagement issues.")
    
    return recommendations
def analyze_retrospectives(data: Dict[str, Any]) -> RetroAnalysisResult:
    """Perform comprehensive retrospective analysis."""
    result = RetroAnalysisResult()
    
    try:
        # Parse retrospective data
        retro_records = data.get("retrospectives", [])
        retros = [RetrospectiveData(record) for record in retro_records]
        
        if not retros:
            raise ValueError("No retrospective data found")
        
        # Sort by sprint number
        retros.sort(key=lambda r: r.sprint_number)
        
        # Basic summary
        result.summary = {
            "total_retrospectives": len(retros),
            "date_range": {
                "first": retros[0].date if retros else "",
                "last": retros[-1].date if retros else "",
                "span_sprints": retros[-1].sprint_number - retros[0].sprint_number + 1 if retros else 0
            },
            "average_duration": statistics.mean([r.duration_minutes for r in retros if r.duration_minutes > 0]),
            "average_attendance": statistics.mean([r.attendance_rate for r in retros]),
        }
        
        # Action item analysis
        result.action_item_analysis = analyze_action_item_completion(retros)
        
        # Theme analysis
        result.theme_analysis = analyze_recurring_themes(retros)
        
        # Improvement trends
        result.improvement_trends = analyze_improvement_trends(retros)
        
        # Generate recommendations
        result.recommendations = generate_recommendations(result)
        
    except Exception as e:
        result.summary = {"error": str(e)}
    
    return result
