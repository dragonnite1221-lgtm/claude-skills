# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from competitor_analyzer_base import *  # noqa: F403,E402


def analyze_competitor_set(
    category: str,
    competitors_data: List[Dict[str, Any]],
    platform: str = 'apple'
) -> Dict[str, Any]:
    """
    Convenience function to analyze a set of competitors.

    Args:
        category: App category
        competitors_data: List of competitor data
        platform: 'apple' or 'google'

    Returns:
        Complete competitive analysis
    """
    analyzer = CompetitorAnalyzer(category, platform)
    return analyzer.compare_competitors(competitors_data)
