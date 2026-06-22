# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from keyword_analyzer_base import *  # noqa: F403,E402


class KeywordAnalyzerMixin0:
    """Analyzes keywords for ASO effectiveness."""
    COMPETITION_THRESHOLDS = {
        'low': 1000,
        'medium': 5000,
        'high': 10000
    }
    VOLUME_CATEGORIES = {
        'very_low': 1000,
        'low': 5000,
        'medium': 20000,
        'high': 100000,
        'very_high': 500000
    }
    def __init__(self):
        """Initialize keyword analyzer."""
        self.analyzed_keywords = {}
    def analyze_keyword(
        self,
        keyword: str,
        search_volume: int = 0,
        competing_apps: int = 0,
        relevance_score: float = 0.0
    ) -> Dict[str, Any]:
        """
        Analyze a single keyword for ASO potential.

        Args:
            keyword: The keyword to analyze
            search_volume: Estimated monthly search volume
            competing_apps: Number of apps competing for this keyword
            relevance_score: Relevance to your app (0.0-1.0)

        Returns:
            Dictionary with keyword analysis
        """
        competition_level = self._calculate_competition_level(competing_apps)
        volume_category = self._categorize_search_volume(search_volume)
        difficulty_score = self._calculate_keyword_difficulty(
            search_volume,
            competing_apps
        )

        # Calculate potential score (0-100)
        potential_score = self._calculate_potential_score(
            search_volume,
            competing_apps,
            relevance_score
        )

        analysis = {
            'keyword': keyword,
            'search_volume': search_volume,
            'volume_category': volume_category,
            'competing_apps': competing_apps,
            'competition_level': competition_level,
            'relevance_score': relevance_score,
            'difficulty_score': difficulty_score,
            'potential_score': potential_score,
            'recommendation': self._generate_recommendation(
                potential_score,
                difficulty_score,
                relevance_score
            ),
            'keyword_length': len(keyword.split()),
            'is_long_tail': len(keyword.split()) >= 3
        }

        self.analyzed_keywords[keyword] = analysis
        return analysis
