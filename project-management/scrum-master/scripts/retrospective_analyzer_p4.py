# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from retrospective_analyzer_base import *  # noqa: F403,E402
# fmt: off
from retrospective_analyzer_p2 import RetrospectiveData  # noqa: E402,E501
from retrospective_analyzer_p3 import _calculate_trend  # noqa: E402,E501
# fmt: on


def analyze_recurring_themes(retros: List[RetrospectiveData]) -> Dict[str, Any]:
    """Identify recurring themes across retrospectives."""
    theme_evolution = defaultdict(list)
    sentiment_evolution = defaultdict(list)
    
    # Track themes over time
    for retro in retros:
        sprint = retro.sprint_number
        
        # Theme tracking
        for theme, count in retro.themes.items():
            theme_evolution[theme].append((sprint, count))
        
        # Sentiment tracking
        for sentiment, score in retro.sentiment_scores.items():
            sentiment_evolution[sentiment].append((sprint, score))
    
    # Identify recurring themes (appear in >50% of retros)
    recurring_threshold = len(retros) * 0.5
    recurring_themes = {}
    
    for theme, occurrences in theme_evolution.items():
        if len(occurrences) >= recurring_threshold:
            sprints, counts = zip(*occurrences)
            recurring_themes[theme] = {
                "frequency": len(occurrences) / len(retros),
                "average_mentions": statistics.mean(counts),
                "trend": _calculate_trend(list(counts)),
                "first_appearance": min(sprints),
                "last_appearance": max(sprints),
                "total_mentions": sum(counts)
            }
    
    # Sentiment trend analysis
    sentiment_trends = {}
    for sentiment, scores_by_sprint in sentiment_evolution.items():
        if len(scores_by_sprint) >= 3:  # Need at least 3 data points
            _, scores = zip(*scores_by_sprint)
            sentiment_trends[sentiment] = {
                "average_score": statistics.mean(scores),
                "trend": _calculate_trend(list(scores)),
                "volatility": statistics.stdev(scores) if len(scores) > 1 else 0.0
            }
    
    # Identify persistent issues (negative themes that recur)
    persistent_issues = []
    for theme, data in recurring_themes.items():
        if theme in ["technical", "process", "external"] and data["frequency"] > 0.6:
            if data["trend"]["direction"] in ["stable", "increasing"]:
                persistent_issues.append({
                    "theme": theme,
                    "frequency": data["frequency"],
                    "severity": data["average_mentions"],
                    "trend": data["trend"]["direction"]
                })
    
    return {
        "recurring_themes": recurring_themes,
        "sentiment_trends": sentiment_trends,
        "persistent_issues": persistent_issues,
        "total_themes_identified": len(theme_evolution),
        "themes_per_retro": sum(len(r.themes) for r in retros) / len(retros) if retros else 0
    }
