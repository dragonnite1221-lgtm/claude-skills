# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from aso_scorer_base import *  # noqa: F403,E402


class ASOScorerMixin2:
    def score_ratings_reviews(self, ratings: Dict[str, Any]) -> float:
        """
        Score ratings and reviews (0-100).

        Evaluates:
        - Average rating
        - Total ratings count
        - Review velocity
        """
        average_rating = ratings.get('average_rating', 0.0)
        total_ratings = ratings.get('total_ratings', 0)
        recent_ratings = ratings.get('recent_ratings_30d', 0)

        # Rating quality score (0-50 points)
        if average_rating >= self.BENCHMARKS['average_rating']['target']:
            rating_quality_score = 50
        elif average_rating >= self.BENCHMARKS['average_rating']['min']:
            # Proportional scoring between min and target
            proportion = (average_rating - self.BENCHMARKS['average_rating']['min']) / \
                        (self.BENCHMARKS['average_rating']['target'] - self.BENCHMARKS['average_rating']['min'])
            rating_quality_score = 30 + (proportion * 20)
        elif average_rating >= 3.0:
            rating_quality_score = 20
        else:
            rating_quality_score = 10

        # Rating volume score (0-30 points)
        if total_ratings >= self.BENCHMARKS['ratings_count']['target']:
            rating_volume_score = 30
        elif total_ratings >= self.BENCHMARKS['ratings_count']['min']:
            # Proportional scoring
            proportion = (total_ratings - self.BENCHMARKS['ratings_count']['min']) / \
                        (self.BENCHMARKS['ratings_count']['target'] - self.BENCHMARKS['ratings_count']['min'])
            rating_volume_score = 15 + (proportion * 15)
        else:
            # Very low volume
            rating_volume_score = (total_ratings / self.BENCHMARKS['ratings_count']['min']) * 15

        # Rating velocity score (0-20 points)
        if recent_ratings > 100:
            velocity_score = 20
        elif recent_ratings > 50:
            velocity_score = 15
        elif recent_ratings > 10:
            velocity_score = 10
        else:
            velocity_score = 5

        total_score = rating_quality_score + rating_volume_score + velocity_score

        return round(min(total_score, 100), 1)
    def score_keyword_performance(self, keyword_performance: Dict[str, Any]) -> float:
        """
        Score keyword ranking performance (0-100).

        Evaluates:
        - Top 10 rankings
        - Top 50 rankings
        - Ranking trends
        """
        top_10_count = keyword_performance.get('top_10', 0)
        top_50_count = keyword_performance.get('top_50', 0)
        top_100_count = keyword_performance.get('top_100', 0)
        improving_keywords = keyword_performance.get('improving_keywords', 0)

        # Top 10 score (0-50 points) - most valuable rankings
        if top_10_count >= self.BENCHMARKS['keywords_top_10']['target']:
            top_10_score = 50
        elif top_10_count >= self.BENCHMARKS['keywords_top_10']['min']:
            proportion = (top_10_count - self.BENCHMARKS['keywords_top_10']['min']) / \
                        (self.BENCHMARKS['keywords_top_10']['target'] - self.BENCHMARKS['keywords_top_10']['min'])
            top_10_score = 25 + (proportion * 25)
        else:
            top_10_score = (top_10_count / self.BENCHMARKS['keywords_top_10']['min']) * 25

        # Top 50 score (0-30 points)
        if top_50_count >= self.BENCHMARKS['keywords_top_50']['target']:
            top_50_score = 30
        elif top_50_count >= self.BENCHMARKS['keywords_top_50']['min']:
            proportion = (top_50_count - self.BENCHMARKS['keywords_top_50']['min']) / \
                        (self.BENCHMARKS['keywords_top_50']['target'] - self.BENCHMARKS['keywords_top_50']['min'])
            top_50_score = 15 + (proportion * 15)
        else:
            top_50_score = (top_50_count / self.BENCHMARKS['keywords_top_50']['min']) * 15

        # Coverage score (0-10 points) - based on top 100
        coverage_score = min((top_100_count / 30) * 10, 10)

        # Trend score (0-10 points) - are rankings improving?
        if improving_keywords > 5:
            trend_score = 10
        elif improving_keywords > 0:
            trend_score = 5
        else:
            trend_score = 0

        total_score = top_10_score + top_50_score + coverage_score + trend_score

        return round(min(total_score, 100), 1)
