# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from localization_helper_base import *  # noqa: F403,E402


class LocalizationHelperMixin3:
    def validate_translations(
        self,
        translated_metadata: Dict[str, str],
        target_language: str,
        platform: str = 'apple'
    ) -> Dict[str, Any]:
        """
        Validate translated metadata for character limits and quality.

        Args:
            translated_metadata: Translated text fields
            target_language: Target language code
            platform: 'apple' or 'google'

        Returns:
            Validation report
        """
        # Platform limits
        if platform == 'apple':
            limits = {'title': 30, 'subtitle': 30, 'description': 4000, 'keywords': 100}
        else:
            limits = {'title': 50, 'short_description': 80, 'description': 4000}

        validation_results = {
            'is_valid': True,
            'field_validations': {},
            'errors': [],
            'warnings': []
        }

        for field, text in translated_metadata.items():
            if field not in limits:
                continue

            actual_length = len(text)
            limit = limits[field]
            is_within_limit = actual_length <= limit

            validation_results['field_validations'][field] = {
                'text': text,
                'length': actual_length,
                'limit': limit,
                'is_valid': is_within_limit,
                'usage_percentage': round((actual_length / limit) * 100, 1)
            }

            if not is_within_limit:
                validation_results['is_valid'] = False
                validation_results['errors'].append(
                    f"{field} exceeds limit: {actual_length}/{limit} characters"
                )

        # Quality checks
        quality_issues = self._check_translation_quality(
            translated_metadata,
            target_language
        )

        validation_results['quality_checks'] = quality_issues

        if quality_issues:
            validation_results['warnings'].extend(
                [f"Quality issue: {issue}" for issue in quality_issues]
            )

        return validation_results
