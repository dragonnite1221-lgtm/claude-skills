# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from review_analyzer_base import *  # noqa: F403,E402


class ReviewAnalyzerMixin3:
    def find_feature_requests(
        self,
        reviews: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Extract feature requests and desired improvements.

        Args:
            reviews: List of review dicts

        Returns:
            Feature request analysis
        """
        feature_requests = []

        for review in reviews:
            text = review.get('text', '').lower()
            rating = review.get('rating', 3)

            # Check for feature request indicators
            is_feature_request = any(
                keyword in text
                for keyword in self.FEATURE_REQUEST_KEYWORDS
            )

            if is_feature_request:
                # Extract the specific request
                request_text = self._extract_feature_request_text(text)

                feature_requests.append({
                    'review_id': review.get('id', ''),
                    'rating': rating,
                    'date': review.get('date', ''),
                    'request_text': request_text,
                    'full_review': text[:200] + '...' if len(text) > 200 else text
                })

        # Cluster similar requests
        clustered_requests = self._cluster_feature_requests(feature_requests)

        # Prioritize based on frequency and rating context
        prioritized_requests = self._prioritize_feature_requests(clustered_requests)

        return {
            'total_feature_requests': len(feature_requests),
            'clustered_requests': clustered_requests,
            'prioritized_requests': prioritized_requests,
            'implementation_recommendations': self._generate_feature_recommendations(
                prioritized_requests
            )
        }
    def track_sentiment_trends(
        self,
        reviews_by_period: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """
        Track sentiment changes over time.

        Args:
            reviews_by_period: Dict of period_name: reviews

        Returns:
            Trend analysis
        """
        trends = []

        for period, reviews in reviews_by_period.items():
            sentiment = self.analyze_sentiment(reviews)

            trends.append({
                'period': period,
                'total_reviews': len(reviews),
                'average_rating': sentiment['average_rating'],
                'positive_percentage': sentiment['sentiment_distribution']['positive'],
                'negative_percentage': sentiment['sentiment_distribution']['negative']
            })

        # Calculate trend direction
        if len(trends) >= 2:
            first_period = trends[0]
            last_period = trends[-1]

            rating_change = last_period['average_rating'] - first_period['average_rating']
            sentiment_change = last_period['positive_percentage'] - first_period['positive_percentage']

            trend_direction = self._determine_trend_direction(
                rating_change,
                sentiment_change
            )
        else:
            trend_direction = 'insufficient_data'

        return {
            'periods_analyzed': len(trends),
            'trend_data': trends,
            'trend_direction': trend_direction,
            'insights': self._generate_trend_insights(trends, trend_direction)
        }
