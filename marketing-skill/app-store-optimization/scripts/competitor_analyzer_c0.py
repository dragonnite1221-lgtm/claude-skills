# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from competitor_analyzer_base import *  # noqa: F403,E402


class CompetitorAnalyzerMixin0:
    """Analyzes competitor apps to identify ASO opportunities."""
    def __init__(self, category: str, platform: str = 'apple'):
        """
        Initialize competitor analyzer.

        Args:
            category: App category (e.g., "Productivity", "Games")
            platform: 'apple' or 'google'
        """
        self.category = category
        self.platform = platform
        self.competitors = []
    def analyze_competitor(
        self,
        app_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze a single competitor's ASO strategy.

        Args:
            app_data: Dictionary with app_name, title, description, rating, ratings_count, keywords

        Returns:
            Comprehensive competitor analysis
        """
        app_name = app_data.get('app_name', '')
        title = app_data.get('title', '')
        description = app_data.get('description', '')
        rating = app_data.get('rating', 0.0)
        ratings_count = app_data.get('ratings_count', 0)
        keywords = app_data.get('keywords', [])

        analysis = {
            'app_name': app_name,
            'title_analysis': self._analyze_title(title),
            'description_analysis': self._analyze_description(description),
            'keyword_strategy': self._extract_keyword_strategy(title, description, keywords),
            'rating_metrics': {
                'rating': rating,
                'ratings_count': ratings_count,
                'rating_quality': self._assess_rating_quality(rating, ratings_count)
            },
            'competitive_strength': self._calculate_competitive_strength(
                rating,
                ratings_count,
                len(description)
            ),
            'key_differentiators': self._identify_differentiators(description)
        }

        self.competitors.append(analysis)
        return analysis
    def compare_competitors(
        self,
        competitors_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Compare multiple competitors and identify patterns.

        Args:
            competitors_data: List of competitor data dictionaries

        Returns:
            Comparative analysis with insights
        """
        # Analyze each competitor
        analyses = []
        for comp_data in competitors_data:
            analysis = self.analyze_competitor(comp_data)
            analyses.append(analysis)

        # Extract common keywords across competitors
        all_keywords = []
        for analysis in analyses:
            all_keywords.extend(analysis['keyword_strategy']['primary_keywords'])

        common_keywords = self._find_common_keywords(all_keywords)

        # Identify keyword gaps (used by some but not all)
        keyword_gaps = self._identify_keyword_gaps(analyses)

        # Rank competitors by strength
        ranked_competitors = sorted(
            analyses,
            key=lambda x: x['competitive_strength'],
            reverse=True
        )

        # Analyze rating distribution
        rating_analysis = self._analyze_rating_distribution(analyses)

        # Identify best practices
        best_practices = self._identify_best_practices(ranked_competitors)

        return {
            'category': self.category,
            'platform': self.platform,
            'competitors_analyzed': len(analyses),
            'ranked_competitors': ranked_competitors,
            'common_keywords': common_keywords,
            'keyword_gaps': keyword_gaps,
            'rating_analysis': rating_analysis,
            'best_practices': best_practices,
            'opportunities': self._identify_opportunities(
                analyses,
                common_keywords,
                keyword_gaps
            )
        }
