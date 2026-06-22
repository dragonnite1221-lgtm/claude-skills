# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from review_analyzer_base import *  # noqa: F403,E402


class ReviewAnalyzerMixin6:
    def _generate_issue_recommendations(
        self,
        categorized_issues: Dict[str, List[Dict[str, Any]]],
        severity_scores: Dict[str, Dict[str, Any]]
    ) -> List[str]:
        """Generate recommendations for addressing issues."""
        recommendations = []

        for category, score_data in severity_scores.items():
            if score_data['priority'] == 'critical':
                recommendations.append(
                    f"URGENT: Address {category} issues immediately - affecting {score_data['percentage']}% of reviews"
                )
            elif score_data['priority'] == 'high':
                recommendations.append(
                    f"HIGH PRIORITY: Focus on {category} issues in next update"
                )

        return recommendations
    def _extract_feature_request_text(self, text: str) -> str:
        """Extract the specific feature request from review text."""
        # Simple extraction - find sentence with feature request keywords
        sentences = text.split('.')
        for sentence in sentences:
            if any(keyword in sentence for keyword in self.FEATURE_REQUEST_KEYWORDS):
                return sentence.strip()
        return text[:100]  # Fallback
    def _cluster_feature_requests(
        self,
        feature_requests: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Cluster similar feature requests."""
        # Simplified clustering - group by common keywords
        clusters = {}

        for request in feature_requests:
            text = request['request_text'].lower()
            # Extract key words
            words = [w for w in text.split() if len(w) > 4]

            # Try to find matching cluster
            matched = False
            for cluster_key in clusters:
                if any(word in cluster_key for word in words[:3]):
                    clusters[cluster_key].append(request)
                    matched = True
                    break

            if not matched and words:
                cluster_key = ' '.join(words[:2])
                clusters[cluster_key] = [request]

        return [
            {'feature_theme': theme, 'request_count': len(requests), 'examples': requests[:3]}
            for theme, requests in clusters.items()
        ]
    def _prioritize_feature_requests(
        self,
        clustered_requests: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Prioritize feature requests by frequency."""
        return sorted(
            clustered_requests,
            key=lambda x: x['request_count'],
            reverse=True
        )[:10]
    def _generate_feature_recommendations(
        self,
        prioritized_requests: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate recommendations for feature requests."""
        recommendations = []

        if prioritized_requests:
            top_request = prioritized_requests[0]
            recommendations.append(
                f"Most requested feature: {top_request['feature_theme']} "
                f"({top_request['request_count']} mentions) - consider for next major release"
            )

        if len(prioritized_requests) > 1:
            recommendations.append(
                f"Also consider: {prioritized_requests[1]['feature_theme']}"
            )

        return recommendations
    def _determine_trend_direction(
        self,
        rating_change: float,
        sentiment_change: float
    ) -> str:
        """Determine overall trend direction."""
        if rating_change > 0.2 and sentiment_change > 5:
            return 'improving'
        elif rating_change < -0.2 and sentiment_change < -5:
            return 'declining'
        else:
            return 'stable'
