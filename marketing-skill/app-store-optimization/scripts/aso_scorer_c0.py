# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from aso_scorer_base import *  # noqa: F403,E402


class ASOScorerMixin0:
    """Calculates overall ASO health score and provides recommendations."""
    WEIGHTS = {
        'metadata_quality': 25,
        'ratings_reviews': 25,
        'keyword_performance': 25,
        'conversion_metrics': 25
    }
    BENCHMARKS = {
        'title_keyword_usage': {'min': 1, 'target': 2},
        'description_length': {'min': 500, 'target': 2000},
        'keyword_density': {'min': 2, 'optimal': 5, 'max': 8},
        'average_rating': {'min': 3.5, 'target': 4.5},
        'ratings_count': {'min': 100, 'target': 5000},
        'keywords_top_10': {'min': 2, 'target': 10},
        'keywords_top_50': {'min': 5, 'target': 20},
        'conversion_rate': {'min': 0.02, 'target': 0.10}
    }
    def __init__(self):
        """Initialize ASO scorer."""
        self.score_breakdown = {}
    def calculate_overall_score(
        self,
        metadata: Dict[str, Any],
        ratings: Dict[str, Any],
        keyword_performance: Dict[str, Any],
        conversion: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive ASO score (0-100).

        Args:
            metadata: Title, description quality metrics
            ratings: Rating average and count
            keyword_performance: Keyword ranking data
            conversion: Impression-to-install metrics

        Returns:
            Overall score with detailed breakdown
        """
        # Calculate component scores
        metadata_score = self.score_metadata_quality(metadata)
        ratings_score = self.score_ratings_reviews(ratings)
        keyword_score = self.score_keyword_performance(keyword_performance)
        conversion_score = self.score_conversion_metrics(conversion)

        # Calculate weighted overall score
        overall_score = (
            metadata_score * (self.WEIGHTS['metadata_quality'] / 100) +
            ratings_score * (self.WEIGHTS['ratings_reviews'] / 100) +
            keyword_score * (self.WEIGHTS['keyword_performance'] / 100) +
            conversion_score * (self.WEIGHTS['conversion_metrics'] / 100)
        )

        # Store breakdown
        self.score_breakdown = {
            'metadata_quality': {
                'score': metadata_score,
                'weight': self.WEIGHTS['metadata_quality'],
                'weighted_contribution': round(metadata_score * (self.WEIGHTS['metadata_quality'] / 100), 1)
            },
            'ratings_reviews': {
                'score': ratings_score,
                'weight': self.WEIGHTS['ratings_reviews'],
                'weighted_contribution': round(ratings_score * (self.WEIGHTS['ratings_reviews'] / 100), 1)
            },
            'keyword_performance': {
                'score': keyword_score,
                'weight': self.WEIGHTS['keyword_performance'],
                'weighted_contribution': round(keyword_score * (self.WEIGHTS['keyword_performance'] / 100), 1)
            },
            'conversion_metrics': {
                'score': conversion_score,
                'weight': self.WEIGHTS['conversion_metrics'],
                'weighted_contribution': round(conversion_score * (self.WEIGHTS['conversion_metrics'] / 100), 1)
            }
        }

        # Generate recommendations
        recommendations = self.generate_recommendations(
            metadata_score,
            ratings_score,
            keyword_score,
            conversion_score
        )

        # Assess overall health
        health_status = self._assess_health_status(overall_score)

        return {
            'overall_score': round(overall_score, 1),
            'health_status': health_status,
            'score_breakdown': self.score_breakdown,
            'recommendations': recommendations,
            'priority_actions': self._prioritize_actions(recommendations),
            'strengths': self._identify_strengths(self.score_breakdown),
            'weaknesses': self._identify_weaknesses(self.score_breakdown)
        }
