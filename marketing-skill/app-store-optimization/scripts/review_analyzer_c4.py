# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from review_analyzer_base import *  # noqa: F403,E402


class ReviewAnalyzerMixin4:
    def generate_response_templates(
        self,
        issue_category: str
    ) -> List[Dict[str, str]]:
        """
        Generate response templates for common review scenarios.

        Args:
            issue_category: Category of issue ('crash', 'feature_request', 'positive', etc.)

        Returns:
            Response templates
        """
        templates = {
            'crash': [
                {
                    'scenario': 'App crash reported',
                    'template': "Thank you for bringing this to our attention. We're sorry you experienced a crash. "
                               "Our team is investigating this issue. Could you please share more details about when "
                               "this occurred (device model, iOS/Android version) by contacting support@[company].com? "
                               "We're committed to fixing this quickly."
                },
                {
                    'scenario': 'Crash already fixed',
                    'template': "Thank you for your feedback. We've identified and fixed this crash issue in version [X.X]. "
                               "Please update to the latest version. If the problem persists, please reach out to "
                               "support@[company].com and we'll help you directly."
                }
            ],
            'bug': [
                {
                    'scenario': 'Bug reported',
                    'template': "Thanks for reporting this bug. We take these issues seriously. Our team is looking into it "
                               "and we'll have a fix in an upcoming update. We appreciate your patience and will notify you "
                               "when it's resolved."
                }
            ],
            'feature_request': [
                {
                    'scenario': 'Feature request received',
                    'template': "Thank you for this suggestion! We're always looking to improve [app_name]. We've added your "
                               "request to our roadmap and will consider it for a future update. Follow us @[social] for "
                               "updates on new features."
                },
                {
                    'scenario': 'Feature already planned',
                    'template': "Great news! This feature is already on our roadmap and we're working on it. Stay tuned for "
                               "updates in the coming months. Thanks for your feedback!"
                }
            ],
            'positive': [
                {
                    'scenario': 'Positive review',
                    'template': "Thank you so much for your kind words! We're thrilled that you're enjoying [app_name]. "
                               "Reviews like yours motivate our team to keep improving. If you ever have suggestions, "
                               "we'd love to hear them!"
                }
            ],
            'negative_general': [
                {
                    'scenario': 'General complaint',
                    'template': "We're sorry to hear you're not satisfied with your experience. We'd like to make this right. "
                               "Please contact us at support@[company].com so we can understand the issue better and help "
                               "you directly. Thank you for giving us a chance to improve."
                }
            ]
        }

        return templates.get(issue_category, templates['negative_general'])
    def _calculate_sentiment_score(self, text: str, rating: int) -> float:
        """Calculate sentiment score (-1 to 1)."""
        # Start with rating-based score
        rating_score = (rating - 3) / 2  # Convert 1-5 to -1 to 1

        # Adjust based on text sentiment
        positive_count = sum(1 for keyword in self.POSITIVE_KEYWORDS if keyword in text)
        negative_count = sum(1 for keyword in self.NEGATIVE_KEYWORDS if keyword in text)

        text_score = (positive_count - negative_count) / 10  # Normalize

        # Weighted average (60% rating, 40% text)
        final_score = (rating_score * 0.6) + (text_score * 0.4)

        return max(min(final_score, 1.0), -1.0)
    def _categorize_sentiment(self, score: float) -> str:
        """Categorize sentiment score."""
        if score > 0.3:
            return 'positive'
        elif score < -0.3:
            return 'negative'
        else:
            return 'neutral'
    def _assess_sentiment_trend(self, distribution: Dict[str, float]) -> str:
        """Assess overall sentiment trend."""
        positive = distribution['positive']
        negative = distribution['negative']

        if positive > 70:
            return 'very_positive'
        elif positive > 50:
            return 'positive'
        elif negative > 30:
            return 'concerning'
        elif negative > 50:
            return 'critical'
        else:
            return 'mixed'
