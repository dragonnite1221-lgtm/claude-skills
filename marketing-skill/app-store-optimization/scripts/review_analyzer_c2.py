# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from review_analyzer_base import *  # noqa: F403,E402


class ReviewAnalyzerMixin2:
    def identify_issues(
        self,
        reviews: List[Dict[str, Any]],
        rating_threshold: int = 3
    ) -> Dict[str, Any]:
        """
        Identify bugs, crashes, and other issues from reviews.

        Args:
            reviews: List of review dicts
            rating_threshold: Only analyze reviews at or below this rating

        Returns:
            Issue identification report
        """
        issues = []

        for review in reviews:
            rating = review.get('rating', 5)
            if rating > rating_threshold:
                continue

            text = review.get('text', '').lower()

            # Check for issue keywords
            mentioned_issues = []
            for keyword in self.ISSUE_KEYWORDS:
                if keyword in text:
                    mentioned_issues.append(keyword)

            if mentioned_issues:
                issues.append({
                    'review_id': review.get('id', ''),
                    'rating': rating,
                    'date': review.get('date', ''),
                    'issue_keywords': mentioned_issues,
                    'text': text[:200] + '...' if len(text) > 200 else text
                })

        # Group by issue type
        issue_frequency = Counter()
        for issue in issues:
            for keyword in issue['issue_keywords']:
                issue_frequency[keyword] += 1

        # Categorize issues
        categorized_issues = self._categorize_issues(issues)

        # Calculate issue severity
        severity_scores = self._calculate_issue_severity(
            categorized_issues,
            len(reviews)
        )

        return {
            'total_issues_found': len(issues),
            'issue_frequency': dict(issue_frequency.most_common(15)),
            'categorized_issues': categorized_issues,
            'severity_scores': severity_scores,
            'top_issues': self._rank_issues_by_severity(severity_scores),
            'recommendations': self._generate_issue_recommendations(
                categorized_issues,
                severity_scores
            )
        }
