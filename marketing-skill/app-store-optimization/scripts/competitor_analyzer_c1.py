# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from competitor_analyzer_base import *  # noqa: F403,E402


class CompetitorAnalyzerMixin1:
    def identify_gaps(
        self,
        your_app_data: Dict[str, Any],
        competitors_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Identify gaps between your app and competitors.

        Args:
            your_app_data: Your app's data
            competitors_data: List of competitor data

        Returns:
            Gap analysis with actionable recommendations
        """
        # Analyze your app
        your_analysis = self.analyze_competitor(your_app_data)

        # Analyze competitors
        competitor_comparison = self.compare_competitors(competitors_data)

        # Identify keyword gaps
        your_keywords = set(your_analysis['keyword_strategy']['primary_keywords'])
        competitor_keywords = set(competitor_comparison['common_keywords'])
        missing_keywords = competitor_keywords - your_keywords

        # Identify rating gap
        avg_competitor_rating = competitor_comparison['rating_analysis']['average_rating']
        rating_gap = avg_competitor_rating - your_analysis['rating_metrics']['rating']

        # Identify description length gap
        avg_competitor_desc_length = sum(
            len(comp['description_analysis']['text'])
            for comp in competitor_comparison['ranked_competitors']
        ) / len(competitor_comparison['ranked_competitors'])
        your_desc_length = len(your_analysis['description_analysis']['text'])
        desc_length_gap = avg_competitor_desc_length - your_desc_length

        return {
            'your_app': your_analysis,
            'keyword_gaps': {
                'missing_keywords': list(missing_keywords)[:10],
                'recommendations': self._generate_keyword_recommendations(missing_keywords)
            },
            'rating_gap': {
                'your_rating': your_analysis['rating_metrics']['rating'],
                'average_competitor_rating': avg_competitor_rating,
                'gap': round(rating_gap, 2),
                'action_items': self._generate_rating_improvement_actions(rating_gap)
            },
            'content_gap': {
                'your_description_length': your_desc_length,
                'average_competitor_length': int(avg_competitor_desc_length),
                'gap': int(desc_length_gap),
                'recommendations': self._generate_content_recommendations(desc_length_gap)
            },
            'competitive_positioning': self._assess_competitive_position(
                your_analysis,
                competitor_comparison
            )
        }
    def _analyze_title(self, title: str) -> Dict[str, Any]:
        """Analyze title structure and keyword usage."""
        parts = re.split(r'[-:|]', title)

        return {
            'title': title,
            'length': len(title),
            'has_brand': len(parts) > 0,
            'has_keywords': len(parts) > 1,
            'components': [part.strip() for part in parts],
            'word_count': len(title.split()),
            'strategy': 'brand_plus_keywords' if len(parts) > 1 else 'brand_only'
        }
    def _analyze_description(self, description: str) -> Dict[str, Any]:
        """Analyze description structure and content."""
        lines = description.split('\n')
        word_count = len(description.split())

        # Check for structural elements
        has_bullet_points = '•' in description or '*' in description
        has_sections = any(line.isupper() for line in lines if len(line) > 0)
        has_call_to_action = any(
            cta in description.lower()
            for cta in ['download', 'try', 'get', 'start', 'join']
        )

        # Extract features mentioned
        features = self._extract_features(description)

        return {
            'text': description,
            'length': len(description),
            'word_count': word_count,
            'structure': {
                'has_bullet_points': has_bullet_points,
                'has_sections': has_sections,
                'has_call_to_action': has_call_to_action
            },
            'features_mentioned': features,
            'readability': 'good' if 50 <= word_count <= 300 else 'needs_improvement'
        }
