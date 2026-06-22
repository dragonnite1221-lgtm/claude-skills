# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from retrospective_analyzer_base import *  # noqa: F403,E402
# fmt: off
from retrospective_analyzer_p2 import RetroAnalysisResult  # noqa: E402,E501
# fmt: on


def format_text_output(result: RetroAnalysisResult) -> str:
    """Format analysis results as readable text report."""
    lines = []
    lines.append("="*60)
    lines.append("RETROSPECTIVE ANALYSIS REPORT")
    lines.append("="*60)
    lines.append("")
    
    if "error" in result.summary:
        lines.append(f"ERROR: {result.summary['error']}")
        return "\n".join(lines)
    
    # Summary section
    summary = result.summary
    lines.append("RETROSPECTIVE SUMMARY")
    lines.append("-"*30)
    lines.append(f"Total Retrospectives: {summary['total_retrospectives']}")
    lines.append(f"Sprint Range: {summary['date_range']['span_sprints']} sprints")
    lines.append(f"Average Duration: {summary.get('average_duration', 0):.0f} minutes")
    lines.append(f"Average Attendance: {summary.get('average_attendance', 0):.1%}")
    lines.append("")
    
    # Action item analysis
    action_analysis = result.action_item_analysis
    lines.append("ACTION ITEM ANALYSIS")
    lines.append("-"*30)
    lines.append(f"Total Action Items: {action_analysis.get('total_action_items', 0)}")
    lines.append(f"Completion Rate: {action_analysis.get('completion_rate', 0):.1%}")
    lines.append(f"Average Completion Time: {action_analysis.get('average_completion_time', 0):.1f} sprints")
    lines.append(f"Overdue Items: {action_analysis.get('overdue_items', 0)} ({action_analysis.get('overdue_rate', 0):.1%})")
    
    priority_analysis = action_analysis.get('priority_analysis', {})
    if priority_analysis:
        lines.append("Priority-based completion rates:")
        for priority, data in priority_analysis.items():
            lines.append(f"  {priority.title()}: {data['completion_rate']:.1%} ({data['completed']}/{data['total']})")
    lines.append("")
    
    # Theme analysis
    theme_analysis = result.theme_analysis
    lines.append("THEME ANALYSIS")
    lines.append("-"*30)
    recurring_themes = theme_analysis.get("recurring_themes", {})
    if recurring_themes:
        lines.append("Top recurring themes:")
        sorted_themes = sorted(recurring_themes.items(), key=lambda x: x[1]['frequency'], reverse=True)
        for theme, data in sorted_themes[:5]:
            lines.append(f"  {theme.replace('_', ' ').title()}: {data['frequency']:.1%} frequency, {data['trend']['direction']} trend")
    
    persistent_issues = theme_analysis.get("persistent_issues", [])
    if persistent_issues:
        lines.append("Persistent issues requiring attention:")
        for issue in persistent_issues:
            lines.append(f"  {issue['theme'].replace('_', ' ').title()}: {issue['frequency']:.1%} frequency")
    lines.append("")
    
    # Improvement trends
    improvement_trends = result.improvement_trends
    if "team_maturity_score" in improvement_trends:
        maturity = improvement_trends["team_maturity_score"]
        lines.append("TEAM MATURITY")
        lines.append("-"*30)
        lines.append(f"Maturity Level: {maturity['level'].replace('_', ' ').title()}")
        lines.append(f"Maturity Score: {maturity['score']:.0f}/100")
        lines.append("")
    
    if "improvement_velocity" in improvement_trends:
        velocity = improvement_trends["improvement_velocity"]
        lines.append("IMPROVEMENT VELOCITY")
        lines.append("-"*30)
        lines.append(f"Velocity: {velocity['velocity'].title()}")
        lines.append(f"Theme Resolution Rate: {velocity.get('theme_resolution_rate', 0):.1%}")
        lines.append("")
    
    # Recommendations
    if result.recommendations:
        lines.append("RECOMMENDATIONS")
        lines.append("-"*30)
        for i, rec in enumerate(result.recommendations, 1):
            lines.append(f"{i}. {rec}")
    
    return "\n".join(lines)
def format_json_output(result: RetroAnalysisResult) -> Dict[str, Any]:
    """Format analysis results as JSON."""
    return {
        "summary": result.summary,
        "action_item_analysis": result.action_item_analysis,
        "theme_analysis": result.theme_analysis,
        "improvement_trends": result.improvement_trends,
        "recommendations": result.recommendations,
    }
