# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from metadata_optimizer_base import *  # noqa: F403,E402


class MetadataOptimizerMixin0:
    """Optimizes app store metadata for maximum discoverability and conversion."""
    CHAR_LIMITS = {
        'apple': {
            'title': 30,
            'subtitle': 30,
            'promotional_text': 170,
            'description': 4000,
            'keywords': 100,
            'whats_new': 4000
        },
        'google': {
            'title': 50,
            'short_description': 80,
            'full_description': 4000
        }
    }
    def __init__(self, platform: str = 'apple'):
        """
        Initialize metadata optimizer.

        Args:
            platform: 'apple' or 'google'
        """
        if platform not in ['apple', 'google']:
            raise ValueError("Platform must be 'apple' or 'google'")

        self.platform = platform
        self.limits = self.CHAR_LIMITS[platform]
    def optimize_title(
        self,
        app_name: str,
        target_keywords: List[str],
        include_brand: bool = True
    ) -> Dict[str, Any]:
        """
        Optimize app title with keyword integration.

        Args:
            app_name: Your app's brand name
            target_keywords: List of keywords to potentially include
            include_brand: Whether to include brand name

        Returns:
            Optimized title options with analysis
        """
        max_length = self.limits['title']

        title_options = []

        # Option 1: Brand name only
        if include_brand:
            option1 = app_name[:max_length]
            title_options.append({
                'title': option1,
                'length': len(option1),
                'remaining_chars': max_length - len(option1),
                'keywords_included': [],
                'strategy': 'brand_only',
                'pros': ['Maximum brand recognition', 'Clean and simple'],
                'cons': ['No keyword targeting', 'Lower discoverability']
            })

        # Option 2: Brand + Primary Keyword
        if target_keywords:
            primary_keyword = target_keywords[0]
            option2 = self._build_title_with_keywords(
                app_name,
                [primary_keyword],
                max_length
            )
            if option2:
                title_options.append({
                    'title': option2,
                    'length': len(option2),
                    'remaining_chars': max_length - len(option2),
                    'keywords_included': [primary_keyword],
                    'strategy': 'brand_plus_primary',
                    'pros': ['Targets main keyword', 'Maintains brand identity'],
                    'cons': ['Limited keyword coverage']
                })

        # Option 3: Brand + Multiple Keywords (if space allows)
        if len(target_keywords) > 1:
            option3 = self._build_title_with_keywords(
                app_name,
                target_keywords[:2],
                max_length
            )
            if option3:
                title_options.append({
                    'title': option3,
                    'length': len(option3),
                    'remaining_chars': max_length - len(option3),
                    'keywords_included': target_keywords[:2],
                    'strategy': 'brand_plus_multiple',
                    'pros': ['Multiple keyword targets', 'Better discoverability'],
                    'cons': ['May feel cluttered', 'Less brand focus']
                })

        # Option 4: Keyword-first approach (for new apps)
        if target_keywords and not include_brand:
            option4 = " ".join(target_keywords[:2])[:max_length]
            title_options.append({
                'title': option4,
                'length': len(option4),
                'remaining_chars': max_length - len(option4),
                'keywords_included': target_keywords[:2],
                'strategy': 'keyword_first',
                'pros': ['Maximum SEO benefit', 'Clear functionality'],
                'cons': ['No brand recognition', 'Generic appearance']
            })

        return {
            'platform': self.platform,
            'max_length': max_length,
            'options': title_options,
            'recommendation': self._recommend_title_option(title_options)
        }
