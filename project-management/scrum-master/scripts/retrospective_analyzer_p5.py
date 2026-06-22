# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from retrospective_analyzer_base import *  # noqa: F403,E402
# fmt: off
from retrospective_analyzer_p2 import RetrospectiveData  # noqa: E402,E501
from retrospective_analyzer_p3 import _calculate_trend  # noqa: E402,E501
# fmt: on


def _calculate_team_maturity(retros: List[RetrospectiveData]) -> Dict[str, Any]:
    """Calculate team maturity based on retrospective patterns."""
    if len(retros) < 3:
        return {"score": 50, "level": "developing"}
    
    maturity_indicators = {
        "action_item_focus": 0,      # Fewer but higher quality action items
        "sentiment_balance": 0,      # Balanced positive/negative sentiment
        "theme_consistency": 0,      # Consistent themes without chaos
        "participation": 0,          # High attendance rates
        "follow_through": 0          # Good action item completion
    }
    
    # Action item focus (quality over quantity)
    avg_action_items = sum(len(r.action_items) for r in retros) / len(retros)
    if 2 <= avg_action_items <= 5:  # Sweet spot
        maturity_indicators["action_item_focus"] = 100
    elif avg_action_items < 2 or avg_action_items > 8:
        maturity_indicators["action_item_focus"] = 30
    else:
        maturity_indicators["action_item_focus"] = 70
    
    # Sentiment balance
    avg_positive = sum(r.sentiment_scores.get("positive", 0) for r in retros) / len(retros)
    avg_negative = sum(r.sentiment_scores.get("negative", 0) for r in retros) / len(retros)
    
    if 0.3 <= avg_positive <= 0.6 and 0.2 <= avg_negative <= 0.4:
        maturity_indicators["sentiment_balance"] = 100
    else:
        maturity_indicators["sentiment_balance"] = 50
    
    # Participation
    avg_attendance = sum(r.attendance_rate for r in retros) / len(retros)
    maturity_indicators["participation"] = min(100, avg_attendance * 100)
    
    # Theme consistency (not too chaotic, not too narrow)
    avg_themes = sum(len(r.themes) for r in retros) / len(retros)
    if 2 <= avg_themes <= 4:
        maturity_indicators["theme_consistency"] = 100
    else:
        maturity_indicators["theme_consistency"] = 70
    
    # Follow-through (estimated from action item patterns)
    # This is simplified - in reality would track actual completion
    recent_retros = retros[-3:] if len(retros) >= 3 else retros
    avg_recent_actions = sum(len(r.action_items) for r in recent_retros) / len(recent_retros)
    
    if avg_recent_actions <= 3:  # Fewer action items might indicate better follow-through
        maturity_indicators["follow_through"] = 80
    else:
        maturity_indicators["follow_through"] = 60
    
    # Calculate overall maturity score
    overall_score = sum(maturity_indicators.values()) / len(maturity_indicators)
    
    if overall_score >= 85:
        level = "high_performing"
    elif overall_score >= 70:
        level = "performing"
    elif overall_score >= 55:
        level = "developing"
    else:
        level = "forming"
    
    return {
        "score": overall_score,
        "level": level,
        "indicators": maturity_indicators
    }
def _assess_retrospective_quality_trend(retros: List[RetrospectiveData]) -> Dict[str, Any]:
    """Assess the quality trend of retrospectives over time."""
    quality_scores = []
    
    for retro in retros:
        score = 0
        
        # Duration appropriateness (60-90 minutes is ideal)
        if 60 <= retro.duration_minutes <= 90:
            score += 25
        elif 45 <= retro.duration_minutes <= 120:
            score += 15
        else:
            score += 5
        
        # Participation
        score += min(25, retro.attendance_rate * 25)
        
        # Balance of content
        went_well_count = len(retro.went_well)
        to_improve_count = len(retro.to_improve)
        total_items = went_well_count + to_improve_count
        
        if total_items > 0:
            balance = min(went_well_count, to_improve_count) / total_items
            score += balance * 25
        
        # Action items quality (not too many, not too few)
        action_count = len(retro.action_items)
        if 2 <= action_count <= 5:
            score += 25
        elif 1 <= action_count <= 7:
            score += 15
        else:
            score += 5
        
        quality_scores.append(score)
    
    if len(quality_scores) >= 2:
        trend = _calculate_trend(quality_scores)
    else:
        trend = {"direction": "insufficient_data", "strength": 0.0}
    
    return {
        "quality_scores": quality_scores,
        "average_quality": statistics.mean(quality_scores),
        "trend": trend,
        "latest_quality": quality_scores[-1] if quality_scores else 0
    }
