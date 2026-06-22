# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from localization_helper_base import *  # noqa: F403,E402


class LocalizationHelperMixin2:
    def adapt_keywords(
        self,
        source_keywords: List[str],
        source_language: str,
        target_language: str,
        target_market: str
    ) -> Dict[str, Any]:
        """
        Adapt keywords for target market (not just direct translation).

        Args:
            source_keywords: Original keywords
            source_language: Source language code
            target_language: Target language code
            target_market: Target market (e.g., 'France', 'Japan')

        Returns:
            Adapted keyword recommendations
        """
        # Cultural adaptation considerations
        cultural_notes = self._get_cultural_keyword_considerations(target_market)

        # Search behavior differences
        search_patterns = self._get_search_patterns(target_market)

        adapted_keywords = []
        for keyword in source_keywords:
            adapted_keywords.append({
                'source_keyword': keyword,
                'adaptation_strategy': self._determine_adaptation_strategy(
                    keyword,
                    target_market
                ),
                'cultural_considerations': cultural_notes.get(keyword, []),
                'priority': 'high' if keyword in source_keywords[:3] else 'medium'
            })

        return {
            'source_language': source_language,
            'target_language': target_language,
            'target_market': target_market,
            'adapted_keywords': adapted_keywords,
            'search_behavior_notes': search_patterns,
            'recommendations': [
                'Use native speakers for keyword research',
                'Test keywords with local users before finalizing',
                'Consider local competitors\' keyword strategies',
                'Monitor search trends in target market'
            ]
        }
