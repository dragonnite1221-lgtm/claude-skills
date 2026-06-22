# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from retrospective_analyzer_base import *  # noqa: F403,E402
# fmt: off
from retrospective_analyzer_p2 import RetrospectiveData  # noqa: E402,E501
from retrospective_analyzer_p3 import _calculate_trend  # noqa: E402,E501
from retrospective_analyzer_p5 import _assess_retrospective_quality_trend, _calculate_team_maturity  # noqa: E402,E501
# fmt: on


def _calculate_improvement_velocity(retros: List[RetrospectiveData]) -> Dict[str, Any]:
    """Calculate how quickly the team improves based on retrospective patterns."""
    if len(retros) < 4:
        return {"velocity": "insufficient_data"}
    
    # Look at theme evolution - are persistent issues being resolved?
    theme_counts = defaultdict(list)
    for retro in retros:
        for theme, count in retro.themes.items():
            theme_counts[theme].append(count)
    
    resolved_themes = 0
    persistent_themes = 0
    
    for theme, counts in theme_counts.items():
        if len(counts) >= 3:
            recent_avg = statistics.mean(counts[-2:])
            early_avg = statistics.mean(counts[:2])
            
            if recent_avg < early_avg * 0.7:  # 30% reduction
                resolved_themes += 1
            elif recent_avg > early_avg * 0.9:  # Still persistent
                persistent_themes += 1
    
    total_themes = resolved_themes + persistent_themes
    if total_themes > 0:
        resolution_rate = resolved_themes / total_themes
    else:
        resolution_rate = 0.5  # Neutral if no data
    
    # Action item completion trends
    if len(retros) >= 4:
        recent_action_density = sum(len(r.action_items) for r in retros[-2:]) / 2
        early_action_density = sum(len(r.action_items) for r in retros[:2]) / 2
        
        action_efficiency = 1.0
        if early_action_density > 0:
            action_efficiency = min(1.0, early_action_density / max(recent_action_density, 1))
    else:
        action_efficiency = 0.5
    
    # Overall velocity score
    velocity_score = (resolution_rate * 0.6) + (action_efficiency * 0.4)
    
    if velocity_score >= 0.8:
        velocity = "high"
    elif velocity_score >= 0.6:
        velocity = "moderate"
    elif velocity_score >= 0.4:
        velocity = "low"
    else:
        velocity = "stagnant"
    
    return {
        "velocity": velocity,
        "velocity_score": velocity_score,
        "theme_resolution_rate": resolution_rate,
        "action_efficiency": action_efficiency,
        "resolved_themes": resolved_themes,
        "persistent_themes": persistent_themes
    }
def analyze_improvement_trends(retros: List[RetrospectiveData]) -> Dict[str, Any]:
    """Analyze improvement trends across retrospectives."""
    if len(retros) < 3:
        return {"error": "Need at least 3 retrospectives for trend analysis"}
    
    # Sort retrospectives by sprint number
    sorted_retros = sorted(retros, key=lambda r: r.sprint_number)
    
    # Track various metrics over time
    metrics_over_time = {
        "action_items_per_retro": [len(r.action_items) for r in sorted_retros],
        "attendance_rate": [r.attendance_rate for r in sorted_retros],
        "duration": [r.duration_minutes for r in sorted_retros],
        "positive_sentiment": [r.sentiment_scores.get("positive", 0) for r in sorted_retros],
        "negative_sentiment": [r.sentiment_scores.get("negative", 0) for r in sorted_retros],
        "total_items_discussed": [r.total_items for r in sorted_retros]
    }
    
    # Calculate trends for each metric
    trend_analysis = {}
    for metric_name, values in metrics_over_time.items():
        if len(values) >= 3:
            trend_analysis[metric_name] = {
                "values": values,
                "trend": _calculate_trend(values),
                "average": statistics.mean(values),
                "latest": values[-1],
                "change_from_first": ((values[-1] - values[0]) / values[0]) if values[0] != 0 else 0
            }
    
    # Action item completion trend
    completion_rates_by_sprint = []
    for i, retro in enumerate(sorted_retros):
        if i > 0:  # Skip first retro as it has no previous action items to complete
            prev_retro = sorted_retros[i-1]
            if prev_retro.action_items:
                completed_count = sum(1 for item in prev_retro.action_items 
                                    if item.is_completed and item.completed_sprint == retro.sprint_number)
                completion_rate = completed_count / len(prev_retro.action_items)
                completion_rates_by_sprint.append(completion_rate)
    
    if completion_rates_by_sprint:
        trend_analysis["action_item_completion"] = {
            "values": completion_rates_by_sprint,
            "trend": _calculate_trend(completion_rates_by_sprint),
            "average": statistics.mean(completion_rates_by_sprint),
            "latest": completion_rates_by_sprint[-1] if completion_rates_by_sprint else 0
        }
    
    # Team maturity indicators
    maturity_score = _calculate_team_maturity(sorted_retros)
    
    return {
        "trend_analysis": trend_analysis,
        "team_maturity_score": maturity_score,
        "retrospective_quality_trend": _assess_retrospective_quality_trend(sorted_retros),
        "improvement_velocity": _calculate_improvement_velocity(sorted_retros)
    }
