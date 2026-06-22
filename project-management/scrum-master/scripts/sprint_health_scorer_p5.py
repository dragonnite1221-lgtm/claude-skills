# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from sprint_health_scorer_base import *  # noqa: F403,E402
# fmt: off
from sprint_health_scorer_p1 import HEALTH_DIMENSIONS, OVERALL_HEALTH_THRESHOLDS  # noqa: E402,E501
from sprint_health_scorer_p2 import HealthScoreResult, SprintHealthData, _score_to_grade, score_commitment_reliability  # noqa: E402,E501
from sprint_health_scorer_p3 import score_blocker_resolution, score_ceremony_engagement, score_scope_stability  # noqa: E402,E501
from sprint_health_scorer_p4 import _generate_detailed_metrics, score_story_completion_distribution, score_velocity_predictability  # noqa: E402,E501
# fmt: on


def _generate_health_recommendations(result: HealthScoreResult) -> List[str]:
    """Generate actionable recommendations based on health scores."""
    recommendations = []
    
    # Overall health recommendations
    if result.overall_score < OVERALL_HEALTH_THRESHOLDS["poor"]:
        recommendations.append("CRITICAL: Sprint health is poor across multiple dimensions. Immediate intervention required.")
    elif result.overall_score < OVERALL_HEALTH_THRESHOLDS["fair"]:
        recommendations.append("Sprint health needs improvement. Focus on top 2-3 problem areas.")
    elif result.overall_score >= OVERALL_HEALTH_THRESHOLDS["excellent"]:
        recommendations.append("Excellent sprint health! Maintain current practices and share learnings with other teams.")
    
    # Dimension-specific recommendations
    for dimension, scores in result.dimension_scores.items():
        if isinstance(scores, dict) and "score" in scores:
            score = scores["score"]
            grade = scores["grade"]
            
            if score < 50:  # Poor performance
                if dimension == "commitment_reliability":
                    recommendations.append("Improve sprint planning accuracy and realistic capacity estimation.")
                elif dimension == "scope_stability":
                    recommendations.append("Reduce mid-sprint scope changes. Strengthen backlog refinement process.")
                elif dimension == "blocker_resolution":
                    recommendations.append("Implement faster blocker escalation and resolution processes.")
                elif dimension == "ceremony_engagement":
                    recommendations.append("Improve ceremony facilitation and team engagement strategies.")
                elif dimension == "story_completion_distribution":
                    recommendations.append("Focus on completing stories fully rather than starting many partially.")
                elif dimension == "velocity_predictability":
                    recommendations.append("Work on consistent estimation and delivery patterns.")
            
            elif score >= 85:  # Excellent performance
                dimension_name = dimension.replace("_", " ").title()
                recommendations.append(f"Excellent {dimension_name}! Document and share best practices.")
    
    return recommendations
def analyze_sprint_health(data: Dict[str, Any]) -> HealthScoreResult:
    """Perform comprehensive sprint health analysis."""
    result = HealthScoreResult()
    
    try:
        # Parse sprint data
        sprint_records = data.get("sprints", [])
        sprints = [SprintHealthData(record) for record in sprint_records]
        
        if not sprints:
            raise ValueError("No sprint data found")
        
        # Sort by sprint number
        sprints.sort(key=lambda s: s.sprint_number)
        
        # Calculate dimension scores
        dimensions = {
            "commitment_reliability": score_commitment_reliability,
            "scope_stability": score_scope_stability,
            "blocker_resolution": score_blocker_resolution,
            "ceremony_engagement": score_ceremony_engagement,
            "story_completion_distribution": score_story_completion_distribution,
            "velocity_predictability": score_velocity_predictability,
        }
        
        weighted_scores = []
        
        for dimension_name, scoring_func in dimensions.items():
            dimension_result = scoring_func(sprints)
            result.dimension_scores[dimension_name] = dimension_result
            
            # Calculate weighted contribution
            weight = HEALTH_DIMENSIONS[dimension_name]["weight"]
            weighted_score = dimension_result["score"] * weight
            weighted_scores.append(weighted_score)
        
        # Calculate overall score
        result.overall_score = sum(weighted_scores)
        result.health_grade = _score_to_grade(result.overall_score)
        
        # Generate detailed metrics
        result.detailed_metrics = _generate_detailed_metrics(sprints)
        
        # Generate recommendations
        result.recommendations = _generate_health_recommendations(result)
        
    except Exception as e:
        result.dimension_scores = {"error": str(e)}
        result.overall_score = 0
    
    return result
