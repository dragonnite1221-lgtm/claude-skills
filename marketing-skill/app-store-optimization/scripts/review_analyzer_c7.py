# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from review_analyzer_base import *  # noqa: F403,E402


class ReviewAnalyzerMixin7:
    def _generate_trend_insights(
        self,
        trends: List[Dict[str, Any]],
        trend_direction: str
    ) -> List[str]:
        """Generate insights from trend analysis."""
        insights = []

        if trend_direction == 'improving':
            insights.append("Positive trend: User satisfaction is increasing over time")
        elif trend_direction == 'declining':
            insights.append("WARNING: User satisfaction is declining - immediate action needed")
        else:
            insights.append("Sentiment is stable - maintain current quality")

        # Review velocity insight
        if len(trends) >= 2:
            recent_reviews = trends[-1]['total_reviews']
            previous_reviews = trends[-2]['total_reviews']

            if recent_reviews > previous_reviews * 1.5:
                insights.append("Review volume increasing - growing user base or recent controversy")

        return insights
