# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from review_analyzer_base import *  # noqa: F403,E402


class ReviewAnalyzerMixin0:
    """Analyzes user reviews for actionable insights."""
    POSITIVE_KEYWORDS = [
        'great', 'awesome', 'excellent', 'amazing', 'love', 'best', 'perfect',
        'fantastic', 'wonderful', 'brilliant', 'outstanding', 'superb'
    ]
    NEGATIVE_KEYWORDS = [
        'bad', 'terrible', 'awful', 'horrible', 'hate', 'worst', 'useless',
        'broken', 'crash', 'bug', 'slow', 'disappointing', 'frustrating'
    ]
    ISSUE_KEYWORDS = [
        'crash', 'bug', 'error', 'broken', 'not working', 'doesnt work',
        'freezes', 'slow', 'laggy', 'glitch', 'problem', 'issue', 'fail'
    ]
    FEATURE_REQUEST_KEYWORDS = [
        'wish', 'would be nice', 'should add', 'need', 'want', 'hope',
        'please add', 'missing', 'lacks', 'feature request'
    ]
    def __init__(self, app_name: str):
        """
        Initialize review analyzer.

        Args:
            app_name: Name of the app
        """
        self.app_name = app_name
        self.reviews = []
        self.analysis_cache = {}
    def analyze_sentiment(
        self,
        reviews: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze sentiment across reviews.

        Args:
            reviews: List of review dicts with 'text', 'rating', 'date'

        Returns:
            Sentiment analysis summary
        """
        self.reviews = reviews

        sentiment_counts = {
            'positive': 0,
            'neutral': 0,
            'negative': 0
        }

        detailed_sentiments = []

        for review in reviews:
            text = review.get('text', '').lower()
            rating = review.get('rating', 3)

            # Calculate sentiment score
            sentiment_score = self._calculate_sentiment_score(text, rating)
            sentiment_category = self._categorize_sentiment(sentiment_score)

            sentiment_counts[sentiment_category] += 1

            detailed_sentiments.append({
                'review_id': review.get('id', ''),
                'rating': rating,
                'sentiment_score': sentiment_score,
                'sentiment': sentiment_category,
                'text_preview': text[:100] + '...' if len(text) > 100 else text
            })

        # Calculate percentages
        total = len(reviews)
        sentiment_distribution = {
            'positive': round((sentiment_counts['positive'] / total) * 100, 1) if total > 0 else 0,
            'neutral': round((sentiment_counts['neutral'] / total) * 100, 1) if total > 0 else 0,
            'negative': round((sentiment_counts['negative'] / total) * 100, 1) if total > 0 else 0
        }

        # Calculate average rating
        avg_rating = sum(r.get('rating', 0) for r in reviews) / total if total > 0 else 0

        return {
            'total_reviews_analyzed': total,
            'average_rating': round(avg_rating, 2),
            'sentiment_distribution': sentiment_distribution,
            'sentiment_counts': sentiment_counts,
            'sentiment_trend': self._assess_sentiment_trend(sentiment_distribution),
            'detailed_sentiments': detailed_sentiments[:50]  # Limit output
        }
