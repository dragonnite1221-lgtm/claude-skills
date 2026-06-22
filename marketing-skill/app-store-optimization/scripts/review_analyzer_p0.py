# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from review_analyzer_base import *  # noqa: F403,E402


def analyze_reviews(
    app_name: str,
    reviews: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Convenience function to perform comprehensive review analysis.

    Args:
        app_name: App name
        reviews: List of review dictionaries

    Returns:
        Complete review analysis
    """
    analyzer = ReviewAnalyzer(app_name)

    return {
        'sentiment_analysis': analyzer.analyze_sentiment(reviews),
        'common_themes': analyzer.extract_common_themes(reviews),
        'issues_identified': analyzer.identify_issues(reviews),
        'feature_requests': analyzer.find_feature_requests(reviews)
    }
