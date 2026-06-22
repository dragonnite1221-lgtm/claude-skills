# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from metadata_optimizer_base import *  # noqa: F403,E402


class MetadataOptimizerMixin1:
    def optimize_description(
        self,
        app_info: Dict[str, Any],
        target_keywords: List[str],
        description_type: str = 'full'
    ) -> Dict[str, Any]:
        """
        Optimize app description with keyword integration and conversion focus.

        Args:
            app_info: Dict with 'name', 'key_features', 'unique_value', 'target_audience'
            target_keywords: List of keywords to integrate naturally
            description_type: 'full', 'short' (Google), 'subtitle' (Apple)

        Returns:
            Optimized description with analysis
        """
        if description_type == 'short' and self.platform == 'google':
            return self._optimize_short_description(app_info, target_keywords)
        elif description_type == 'subtitle' and self.platform == 'apple':
            return self._optimize_subtitle(app_info, target_keywords)
        else:
            return self._optimize_full_description(app_info, target_keywords)
    def optimize_keyword_field(
        self,
        target_keywords: List[str],
        app_title: str = "",
        app_description: str = ""
    ) -> Dict[str, Any]:
        """
        Optimize Apple's 100-character keyword field.

        Rules:
        - No spaces between commas
        - No plural forms if singular exists
        - No duplicates
        - Keywords in title/subtitle are already indexed

        Args:
            target_keywords: List of target keywords
            app_title: Current app title (to avoid duplication)
            app_description: Current description (to check coverage)

        Returns:
            Optimized keyword field (comma-separated, no spaces)
        """
        if self.platform != 'apple':
            return {'error': 'Keyword field optimization only applies to Apple App Store'}

        max_length = self.limits['keywords']

        # Extract words already in title (these don't need to be in keyword field)
        title_words = set(app_title.lower().split()) if app_title else set()

        # Process keywords
        processed_keywords = []
        for keyword in target_keywords:
            keyword_lower = keyword.lower().strip()

            # Skip if already in title
            if keyword_lower in title_words:
                continue

            # Remove duplicates and process
            words = keyword_lower.split()
            for word in words:
                if word not in processed_keywords and word not in title_words:
                    processed_keywords.append(word)

        # Remove plurals if singular exists
        deduplicated = self._remove_plural_duplicates(processed_keywords)

        # Build keyword field within 100 character limit
        keyword_field = self._build_keyword_field(deduplicated, max_length)

        # Calculate keyword density in description
        density = self._calculate_coverage(target_keywords, app_description)

        return {
            'keyword_field': keyword_field,
            'length': len(keyword_field),
            'remaining_chars': max_length - len(keyword_field),
            'keywords_included': keyword_field.split(','),
            'keywords_count': len(keyword_field.split(',')),
            'keywords_excluded': [kw for kw in target_keywords if kw.lower() not in keyword_field],
            'description_coverage': density,
            'optimization_tips': [
                'Keywords in title are auto-indexed - no need to repeat',
                'Use singular forms only (Apple indexes plurals automatically)',
                'No spaces between commas to maximize character usage',
                'Update keyword field with each app update to test variations'
            ]
        }
