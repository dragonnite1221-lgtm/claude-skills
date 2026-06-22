# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from sprint_health_scorer_base import *  # noqa: F403,E402
# fmt: off
from sprint_health_scorer_p1 import HEALTH_DIMENSIONS  # noqa: E402,E501
from sprint_health_scorer_p2 import SprintHealthData, _calculate_dimension_score, _score_to_grade  # noqa: E402,E501
# fmt: on


def score_story_completion_distribution(sprints: List[SprintHealthData]) -> Dict[str, Any]:
    """Score how well stories are completed vs. partially done."""
    if not sprints:
        return {"score": 0, "grade": "insufficient_data"}
    
    completion_ratios = []
    story_analysis = {
        "total_stories": 0,
        "completed_stories": 0,
        "blocked_stories": 0,
        "partial_completion": 0
    }
    
    for sprint in sprints:
        if sprint.stories:
            sprint_completion = sprint.story_completion_ratio
            completion_ratios.append(sprint_completion)
            
            story_analysis["total_stories"] += len(sprint.stories)
            story_analysis["completed_stories"] += sum(1 for s in sprint.stories if s.is_completed)
            story_analysis["blocked_stories"] += sum(1 for s in sprint.stories if s.is_blocked)
    
    if not completion_ratios:
        return {"score": 50, "grade": "fair", "details": "No story data available"}
    
    avg_completion_ratio = statistics.mean(completion_ratios)
    
    config = HEALTH_DIMENSIONS["story_completion_distribution"]
    score = _calculate_dimension_score(avg_completion_ratio, config)
    
    # Penalty for high number of blocked stories
    if story_analysis["total_stories"] > 0:
        blocked_ratio = story_analysis["blocked_stories"] / story_analysis["total_stories"]
        if blocked_ratio > 0.20:  # More than 20% blocked
            score = max(0, score - (blocked_ratio - 0.20) * 100)
    
    return {
        "score": score,
        "grade": _score_to_grade(score),
        "average_completion_ratio": avg_completion_ratio,
        "story_analysis": story_analysis,
        "details": f"Average story completion: {avg_completion_ratio:.1%}"
    }
def score_velocity_predictability(sprints: List[SprintHealthData]) -> Dict[str, Any]:
    """Score velocity predictability based on coefficient of variation."""
    if len(sprints) < 2:
        return {"score": 50, "grade": "fair", "details": "Insufficient sprints for predictability analysis"}
    
    velocities = [sprint.completed_points for sprint in sprints]
    mean_velocity = statistics.mean(velocities)
    
    if mean_velocity == 0:
        return {"score": 0, "grade": "poor", "details": "No velocity recorded"}
    
    velocity_cv = statistics.stdev(velocities) / mean_velocity
    
    # Lower CV is better for predictability
    config = HEALTH_DIMENSIONS["velocity_predictability"]
    
    if velocity_cv <= config["excellent_threshold"]:
        score = 95
    elif velocity_cv <= config["good_threshold"]:
        score = 80 - (velocity_cv - config["excellent_threshold"]) * 150
    elif velocity_cv <= config["poor_threshold"]:
        score = 60 - (velocity_cv - config["good_threshold"]) * 100
    else:
        score = max(20, 40 - (velocity_cv - config["poor_threshold"]) * 50)
    
    return {
        "score": score,
        "grade": _score_to_grade(score),
        "coefficient_of_variation": velocity_cv,
        "mean_velocity": mean_velocity,
        "velocity_std_dev": statistics.stdev(velocities),
        "details": f"Velocity CV: {velocity_cv:.1%} (lower is more predictable)"
    }
def _generate_detailed_metrics(sprints: List[SprintHealthData]) -> Dict[str, Any]:
    """Generate detailed metrics for analysis."""
    metrics = {
        "sprint_count": len(sprints),
        "date_range": {
            "start": sprints[0].start_date if sprints else "",
            "end": sprints[-1].end_date if sprints else "",
        },
        "team_metrics": {},
        "story_metrics": {},
        "blocker_metrics": {},
    }
    
    if not sprints:
        return metrics
    
    # Team metrics
    team_sizes = [sprint.team_size for sprint in sprints if sprint.team_size > 0]
    if team_sizes:
        metrics["team_metrics"] = {
            "average_team_size": statistics.mean(team_sizes),
            "team_size_stability": statistics.stdev(team_sizes) if len(team_sizes) > 1 else 0,
        }
    
    # Story metrics
    all_stories = []
    for sprint in sprints:
        all_stories.extend(sprint.stories)
    
    if all_stories:
        story_points = [story.points for story in all_stories if story.points > 0]
        metrics["story_metrics"] = {
            "total_stories": len(all_stories),
            "average_story_points": statistics.mean(story_points) if story_points else 0,
            "completed_stories": sum(1 for story in all_stories if story.is_completed),
            "blocked_stories": sum(1 for story in all_stories if story.is_blocked),
        }
    
    # Blocker metrics
    all_blockers = []
    for sprint in sprints:
        all_blockers.extend(sprint.blockers)
    
    if all_blockers:
        resolution_times = [b.get("resolution_days", 0) for b in all_blockers if b.get("resolution_days", 0) > 0]
        metrics["blocker_metrics"] = {
            "total_blockers": len(all_blockers),
            "resolved_blockers": len(resolution_times),
            "average_resolution_days": statistics.mean(resolution_times) if resolution_times else 0,
        }
    
    return metrics
