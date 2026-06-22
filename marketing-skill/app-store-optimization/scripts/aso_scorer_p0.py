# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from aso_scorer_base import *  # noqa: F403,E402


def calculate_aso_score(
    metadata: Dict[str, Any],
    ratings: Dict[str, Any],
    keyword_performance: Dict[str, Any],
    conversion: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Convenience function to calculate ASO score.

    Args:
        metadata: Metadata quality metrics
        ratings: Ratings data
        keyword_performance: Keyword ranking data
        conversion: Conversion metrics

    Returns:
        Complete ASO score report
    """
    scorer = ASOScorer()
    return scorer.calculate_overall_score(
        metadata,
        ratings,
        keyword_performance,
        conversion
    )
