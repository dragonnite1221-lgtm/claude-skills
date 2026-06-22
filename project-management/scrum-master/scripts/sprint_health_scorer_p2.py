# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from sprint_health_scorer_base import *  # noqa: F403,E402
# fmt: off
from sprint_health_scorer_p1 import HEALTH_DIMENSIONS, OVERALL_HEALTH_THRESHOLDS, Story  # noqa: E402,E501
# fmt: on


class SprintHealthData:
    """Comprehensive sprint health data model."""
    
    def __init__(self, data: Dict[str, Any]):
        self.sprint_number: int = data.get("sprint_number", 0)
        self.sprint_name: str = data.get("sprint_name", "")
        self.start_date: str = data.get("start_date", "")
        self.end_date: str = data.get("end_date", "")
        self.team_size: int = data.get("team_size", 0)
        self.working_days: int = data.get("working_days", 10)
        
        # Commitment and delivery
        self.planned_points: int = data.get("planned_points", 0)
        self.completed_points: int = data.get("completed_points", 0)
        self.added_points: int = data.get("added_points", 0)
        self.removed_points: int = data.get("removed_points", 0)
        
        # Stories
        story_data = data.get("stories", [])
        self.stories: List[Story] = [Story(story) for story in story_data]
        
        # Blockers
        self.blockers: List[Dict[str, Any]] = data.get("blockers", [])
        
        # Ceremonies
        self.ceremonies: Dict[str, Any] = data.get("ceremonies", {})
        
        # Calculate derived metrics
        self._calculate_derived_metrics()
    
    def _calculate_derived_metrics(self):
        """Calculate derived health metrics."""
        # Commitment reliability
        self.commitment_ratio = (
            self.completed_points / max(self.planned_points, 1)
        )
        
        # Scope change
        total_scope_change = self.added_points + self.removed_points
        self.scope_change_ratio = total_scope_change / max(self.planned_points, 1)
        
        # Story completion distribution
        total_stories = len(self.stories)
        if total_stories > 0:
            completed_stories = sum(1 for story in self.stories if story.is_completed)
            self.story_completion_ratio = completed_stories / total_stories
        else:
            self.story_completion_ratio = 0.0
        
        # Blocked stories analysis
        blocked_stories = [story for story in self.stories if story.is_blocked]
        self.blocked_stories_count = len(blocked_stories)
        self.blocked_points = sum(story.points for story in blocked_stories)
class HealthScoreResult:
    """Complete health scoring results."""
    
    def __init__(self):
        self.dimension_scores: Dict[str, Dict[str, Any]] = {}
        self.overall_score: float = 0.0
        self.health_grade: str = ""
        self.trend_analysis: Dict[str, Any] = {}
        self.recommendations: List[str] = []
        self.detailed_metrics: Dict[str, Any] = {}
def _calculate_dimension_score(value: float, config: Dict[str, Any]) -> float:
    """Calculate dimension score based on thresholds."""
    if value >= config["excellent_threshold"]:
        return 95
    elif value >= config["good_threshold"]:
        # Linear interpolation between good and excellent
        range_size = config["excellent_threshold"] - config["good_threshold"]
        position = (value - config["good_threshold"]) / range_size
        return 80 + (position * 15)
    elif value >= config["poor_threshold"]:
        # Linear interpolation between poor and good
        range_size = config["good_threshold"] - config["poor_threshold"]
        position = (value - config["poor_threshold"]) / range_size
        return 50 + (position * 30)
    else:
        # Below poor threshold
        return max(20, 50 - (config["poor_threshold"] - value) * 100)
def _score_to_grade(score: float) -> str:
    """Convert numerical score to letter grade."""
    if score >= OVERALL_HEALTH_THRESHOLDS["excellent"]:
        return "excellent"
    elif score >= OVERALL_HEALTH_THRESHOLDS["good"]:
        return "good"
    elif score >= OVERALL_HEALTH_THRESHOLDS["fair"]:
        return "fair"
    else:
        return "poor"
def score_commitment_reliability(sprints: List[SprintHealthData]) -> Dict[str, Any]:
    """Score commitment reliability across sprints."""
    if not sprints:
        return {"score": 0, "grade": "insufficient_data"}
    
    commitment_ratios = [sprint.commitment_ratio for sprint in sprints]
    avg_commitment = statistics.mean(commitment_ratios)
    consistency = 1.0 - (statistics.stdev(commitment_ratios) if len(commitment_ratios) > 1 else 0)
    
    # Score based on average achievement and consistency
    config = HEALTH_DIMENSIONS["commitment_reliability"]
    base_score = _calculate_dimension_score(avg_commitment, config)
    
    # Penalty for inconsistency
    consistency_bonus = min(10, consistency * 10)
    final_score = min(100, base_score + consistency_bonus)
    
    return {
        "score": final_score,
        "grade": _score_to_grade(final_score),
        "average_commitment": avg_commitment,
        "consistency": consistency,
        "commitment_ratios": commitment_ratios,
        "details": f"Average commitment: {avg_commitment:.1%}, Consistency: {consistency:.1%}"
    }
