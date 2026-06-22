# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from sprint_health_scorer_base import *  # noqa: F403,E402
# fmt: off
from sprint_health_scorer_p1 import HEALTH_DIMENSIONS  # noqa: E402,E501
from sprint_health_scorer_p2 import SprintHealthData, _calculate_dimension_score, _score_to_grade  # noqa: E402,E501
# fmt: on


def score_scope_stability(sprints: List[SprintHealthData]) -> Dict[str, Any]:
    """Score scope stability (low scope change is better)."""
    if not sprints:
        return {"score": 0, "grade": "insufficient_data"}
    
    scope_change_ratios = [sprint.scope_change_ratio for sprint in sprints]
    avg_scope_change = statistics.mean(scope_change_ratios)
    
    # For scope change, lower is better, so invert the scoring
    config = HEALTH_DIMENSIONS["scope_stability"]
    
    if avg_scope_change <= config["excellent_threshold"]:
        score = 90 + (config["excellent_threshold"] - avg_scope_change) * 200
    elif avg_scope_change <= config["good_threshold"]:
        score = 70 + (config["good_threshold"] - avg_scope_change) * 200
    elif avg_scope_change <= config["poor_threshold"]:
        score = 40 + (config["poor_threshold"] - avg_scope_change) * 200
    else:
        score = max(0, 40 - (avg_scope_change - config["poor_threshold"]) * 100)
    
    score = min(100, max(0, score))
    
    return {
        "score": score,
        "grade": _score_to_grade(score),
        "average_scope_change": avg_scope_change,
        "scope_change_ratios": scope_change_ratios,
        "details": f"Average scope change: {avg_scope_change:.1%}"
    }
def score_blocker_resolution(sprints: List[SprintHealthData]) -> Dict[str, Any]:
    """Score blocker resolution efficiency."""
    if not sprints:
        return {"score": 0, "grade": "insufficient_data"}
    
    all_blockers = []
    for sprint in sprints:
        all_blockers.extend(sprint.blockers)
    
    if not all_blockers:
        return {
            "score": 100,
            "grade": "excellent",
            "average_resolution_time": 0,
            "details": "No blockers reported"
        }
    
    # Calculate average resolution time
    resolution_times = []
    for blocker in all_blockers:
        resolution_time = blocker.get("resolution_days", 0)
        if resolution_time > 0:
            resolution_times.append(resolution_time)
    
    if not resolution_times:
        return {"score": 50, "grade": "fair", "details": "No resolution time data"}
    
    avg_resolution_time = statistics.mean(resolution_times)
    
    # Score based on resolution time (lower is better)
    config = HEALTH_DIMENSIONS["blocker_resolution"]
    
    if avg_resolution_time <= config["excellent_threshold"]:
        score = 95
    elif avg_resolution_time <= config["good_threshold"]:
        score = 80 - (avg_resolution_time - config["excellent_threshold"]) * 10
    elif avg_resolution_time <= config["poor_threshold"]:
        score = 60 - (avg_resolution_time - config["good_threshold"]) * 5
    else:
        score = max(20, 40 - (avg_resolution_time - config["poor_threshold"]) * 3)
    
    return {
        "score": score,
        "grade": _score_to_grade(score),
        "average_resolution_time": avg_resolution_time,
        "total_blockers": len(all_blockers),
        "resolved_blockers": len(resolution_times),
        "details": f"Average resolution: {avg_resolution_time:.1f} days from {len(all_blockers)} blockers"
    }
def score_ceremony_engagement(sprints: List[SprintHealthData]) -> Dict[str, Any]:
    """Score team engagement in scrum ceremonies."""
    if not sprints:
        return {"score": 0, "grade": "insufficient_data"}
    
    ceremony_scores = []
    ceremony_details = {}
    
    for sprint in sprints:
        ceremonies = sprint.ceremonies
        sprint_ceremony_scores = []
        
        for ceremony_name, ceremony_data in ceremonies.items():
            if isinstance(ceremony_data, dict):
                attendance_rate = ceremony_data.get("attendance_rate", 0)
                engagement_score = ceremony_data.get("engagement_score", 0)
                
                # Weight attendance more heavily than engagement
                ceremony_score = (attendance_rate * 0.7) + (engagement_score * 0.3)
                sprint_ceremony_scores.append(ceremony_score)
                
                if ceremony_name not in ceremony_details:
                    ceremony_details[ceremony_name] = []
                ceremony_details[ceremony_name].append({
                    "sprint": sprint.sprint_number,
                    "attendance": attendance_rate,
                    "engagement": engagement_score,
                    "score": ceremony_score
                })
        
        if sprint_ceremony_scores:
            ceremony_scores.append(statistics.mean(sprint_ceremony_scores))
    
    if not ceremony_scores:
        return {"score": 50, "grade": "fair", "details": "No ceremony data available"}
    
    avg_ceremony_score = statistics.mean(ceremony_scores)
    
    config = HEALTH_DIMENSIONS["ceremony_engagement"]
    score = _calculate_dimension_score(avg_ceremony_score, config)
    
    return {
        "score": score,
        "grade": _score_to_grade(score),
        "average_ceremony_score": avg_ceremony_score,
        "ceremony_details": ceremony_details,
        "details": f"Average ceremony engagement: {avg_ceremony_score:.1%}"
    }
