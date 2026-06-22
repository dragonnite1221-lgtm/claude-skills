# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from metadata_optimizer_base import *  # noqa: F403,E402


class MetadataOptimizerMixin2:
    def validate_character_limits(
        self,
        metadata: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Validate all metadata fields against platform character limits.

        Args:
            metadata: Dictionary of field_name: value

        Returns:
            Validation report with errors and warnings
        """
        validation_results = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'field_status': {}
        }

        for field_name, value in metadata.items():
            if field_name not in self.limits:
                validation_results['warnings'].append(
                    f"Unknown field '{field_name}' for {self.platform} platform"
                )
                continue

            max_length = self.limits[field_name]
            actual_length = len(value)
            remaining = max_length - actual_length

            field_status = {
                'value': value,
                'length': actual_length,
                'limit': max_length,
                'remaining': remaining,
                'is_valid': actual_length <= max_length,
                'usage_percentage': round((actual_length / max_length) * 100, 1)
            }

            validation_results['field_status'][field_name] = field_status

            if actual_length > max_length:
                validation_results['is_valid'] = False
                validation_results['errors'].append(
                    f"'{field_name}' exceeds limit: {actual_length}/{max_length} chars"
                )
            elif remaining > max_length * 0.2:  # More than 20% unused
                validation_results['warnings'].append(
                    f"'{field_name}' under-utilizes space: {remaining} chars remaining"
                )

        return validation_results
    def calculate_keyword_density(
        self,
        text: str,
        target_keywords: List[str]
    ) -> Dict[str, Any]:
        """
        Calculate keyword density in text.

        Args:
            text: Text to analyze
            target_keywords: Keywords to check

        Returns:
            Density analysis
        """
        text_lower = text.lower()
        total_words = len(text_lower.split())

        keyword_densities = {}
        for keyword in target_keywords:
            keyword_lower = keyword.lower()
            count = text_lower.count(keyword_lower)
            density = (count / total_words * 100) if total_words > 0 else 0

            keyword_densities[keyword] = {
                'occurrences': count,
                'density_percentage': round(density, 2),
                'status': self._assess_density(density)
            }

        # Overall assessment
        total_keyword_occurrences = sum(kw['occurrences'] for kw in keyword_densities.values())
        overall_density = (total_keyword_occurrences / total_words * 100) if total_words > 0 else 0

        return {
            'total_words': total_words,
            'keyword_densities': keyword_densities,
            'overall_keyword_density': round(overall_density, 2),
            'assessment': self._assess_overall_density(overall_density),
            'recommendations': self._generate_density_recommendations(keyword_densities)
        }
    def _build_title_with_keywords(
        self,
        app_name: str,
        keywords: List[str],
        max_length: int
    ) -> Optional[str]:
        """Build title combining app name and keywords within limit."""
        separators = [' - ', ': ', ' | ']

        for sep in separators:
            for kw in keywords:
                title = f"{app_name}{sep}{kw}"
                if len(title) <= max_length:
                    return title

        return None
