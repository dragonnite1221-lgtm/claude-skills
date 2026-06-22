# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from review_analyzer_base import *  # noqa: F403,E402


class ReviewAnalyzerMixin5:
    def _categorize_themes(
        self,
        common_words: List[Dict[str, Any]],
        common_phrases: List[Dict[str, Any]]
    ) -> Dict[str, List[str]]:
        """Categorize themes from words and phrases."""
        themes = {
            'features': [],
            'performance': [],
            'usability': [],
            'support': [],
            'pricing': []
        }

        # Keywords for each category
        feature_keywords = {'feature', 'functionality', 'option', 'tool'}
        performance_keywords = {'fast', 'slow', 'crash', 'lag', 'speed', 'performance'}
        usability_keywords = {'easy', 'difficult', 'intuitive', 'confusing', 'interface', 'design'}
        support_keywords = {'support', 'help', 'customer', 'service', 'response'}
        pricing_keywords = {'price', 'cost', 'expensive', 'cheap', 'subscription', 'free'}

        for word_data in common_words:
            word = word_data['word']
            if any(kw in word for kw in feature_keywords):
                themes['features'].append(word)
            elif any(kw in word for kw in performance_keywords):
                themes['performance'].append(word)
            elif any(kw in word for kw in usability_keywords):
                themes['usability'].append(word)
            elif any(kw in word for kw in support_keywords):
                themes['support'].append(word)
            elif any(kw in word for kw in pricing_keywords):
                themes['pricing'].append(word)

        return {k: v for k, v in themes.items() if v}  # Remove empty categories
    def _generate_theme_insights(self, themes: Dict[str, List[str]]) -> List[str]:
        """Generate insights from themes."""
        insights = []

        for category, keywords in themes.items():
            if keywords:
                insights.append(
                    f"{category.title()}: Users frequently mention {', '.join(keywords[:3])}"
                )

        return insights[:5]
    def _categorize_issues(self, issues: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Categorize issues by type."""
        categories = {
            'crashes': [],
            'bugs': [],
            'performance': [],
            'compatibility': []
        }

        for issue in issues:
            keywords = issue['issue_keywords']

            if 'crash' in keywords or 'freezes' in keywords:
                categories['crashes'].append(issue)
            elif 'bug' in keywords or 'error' in keywords or 'broken' in keywords:
                categories['bugs'].append(issue)
            elif 'slow' in keywords or 'laggy' in keywords:
                categories['performance'].append(issue)
            else:
                categories['compatibility'].append(issue)

        return {k: v for k, v in categories.items() if v}
    def _calculate_issue_severity(
        self,
        categorized_issues: Dict[str, List[Dict[str, Any]]],
        total_reviews: int
    ) -> Dict[str, Dict[str, Any]]:
        """Calculate severity scores for each issue category."""
        severity_scores = {}

        for category, issues in categorized_issues.items():
            count = len(issues)
            percentage = (count / total_reviews) * 100 if total_reviews > 0 else 0

            # Calculate average rating of affected reviews
            avg_rating = sum(i['rating'] for i in issues) / count if count > 0 else 0

            # Severity score (0-100)
            severity = min((percentage * 10) + ((5 - avg_rating) * 10), 100)

            severity_scores[category] = {
                'count': count,
                'percentage': round(percentage, 2),
                'average_rating': round(avg_rating, 2),
                'severity_score': round(severity, 1),
                'priority': 'critical' if severity > 70 else ('high' if severity > 40 else 'medium')
            }

        return severity_scores
    def _rank_issues_by_severity(
        self,
        severity_scores: Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Rank issues by severity score."""
        ranked = sorted(
            [{'category': cat, **data} for cat, data in severity_scores.items()],
            key=lambda x: x['severity_score'],
            reverse=True
        )
        return ranked
