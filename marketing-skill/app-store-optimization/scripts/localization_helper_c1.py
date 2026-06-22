# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from localization_helper_base import *  # noqa: F403,E402


class LocalizationHelperMixin1:
    def translate_metadata(
        self,
        source_metadata: Dict[str, str],
        source_language: str,
        target_language: str,
        platform: str = 'apple'
    ) -> Dict[str, Any]:
        """
        Generate localized metadata with character limit considerations.

        Args:
            source_metadata: Original metadata (title, description, etc.)
            source_language: Source language code (e.g., 'en')
            target_language: Target language code (e.g., 'es')
            platform: 'apple' or 'google'

        Returns:
            Localized metadata with character limit validation
        """
        # Get character multiplier
        target_lang_code = target_language.split('-')[0]
        char_multiplier = self.CHAR_MULTIPLIERS.get(target_lang_code, 1.0)

        # Platform-specific limits
        if platform == 'apple':
            limits = {'title': 30, 'subtitle': 30, 'description': 4000, 'keywords': 100}
        else:
            limits = {'title': 50, 'short_description': 80, 'description': 4000}

        localized_metadata = {}
        warnings = []

        for field, text in source_metadata.items():
            if field not in limits:
                continue

            # Estimate target length
            estimated_length = int(len(text) * char_multiplier)
            limit = limits[field]

            localized_metadata[field] = {
                'original_text': text,
                'original_length': len(text),
                'estimated_target_length': estimated_length,
                'character_limit': limit,
                'fits_within_limit': estimated_length <= limit,
                'translation_notes': self._get_translation_notes(
                    field,
                    target_language,
                    estimated_length,
                    limit
                )
            }

            if estimated_length > limit:
                warnings.append(
                    f"{field}: Estimated length ({estimated_length}) may exceed limit ({limit}) - "
                    f"condensing may be required"
                )

        return {
            'source_language': source_language,
            'target_language': target_language,
            'platform': platform,
            'localized_fields': localized_metadata,
            'character_multiplier': char_multiplier,
            'warnings': warnings,
            'recommendations': self._generate_translation_recommendations(
                target_language,
                warnings
            )
        }
