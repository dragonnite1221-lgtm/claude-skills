# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from keyword_analyzer_base import *  # noqa: F403,E402


def analyze_keyword_set(keywords_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Convenience function to analyze a set of keywords.

    Args:
        keywords_data: List of keyword data dictionaries

    Returns:
        Complete analysis report
    """
    analyzer = KeywordAnalyzer()
    return analyzer.compare_keywords(keywords_data)
