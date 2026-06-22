# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from metadata_optimizer_base import *  # noqa: F403,E402


class MetadataOptimizerMixin3:
    def _optimize_short_description(
        self,
        app_info: Dict[str, Any],
        target_keywords: List[str]
    ) -> Dict[str, Any]:
        """Optimize Google Play short description (80 chars)."""
        max_length = self.limits['short_description']

        # Focus on unique value proposition with primary keyword
        unique_value = app_info.get('unique_value', '')
        primary_keyword = target_keywords[0] if target_keywords else ''

        # Template: [Primary Keyword] - [Unique Value]
        short_desc = f"{primary_keyword.title()} - {unique_value}"[:max_length]

        return {
            'short_description': short_desc,
            'length': len(short_desc),
            'remaining_chars': max_length - len(short_desc),
            'keywords_included': [primary_keyword] if primary_keyword in short_desc.lower() else [],
            'strategy': 'keyword_value_proposition'
        }
    def _optimize_subtitle(
        self,
        app_info: Dict[str, Any],
        target_keywords: List[str]
    ) -> Dict[str, Any]:
        """Optimize Apple App Store subtitle (30 chars)."""
        max_length = self.limits['subtitle']

        # Very concise - primary keyword or key feature
        primary_keyword = target_keywords[0] if target_keywords else ''
        key_feature = app_info.get('key_features', [''])[0] if app_info.get('key_features') else ''

        options = [
            primary_keyword[:max_length],
            key_feature[:max_length],
            f"{primary_keyword} App"[:max_length]
        ]

        return {
            'subtitle_options': [opt for opt in options if opt],
            'max_length': max_length,
            'recommendation': options[0] if options else ''
        }
    def _optimize_full_description(
        self,
        app_info: Dict[str, Any],
        target_keywords: List[str]
    ) -> Dict[str, Any]:
        """Optimize full app description (4000 chars for both platforms)."""
        max_length = self.limits.get('description', self.limits.get('full_description', 4000))

        # Structure: Hook → Features → Benefits → Social Proof → CTA
        sections = []

        # Hook (with primary keyword)
        primary_keyword = target_keywords[0] if target_keywords else ''
        unique_value = app_info.get('unique_value', '')
        hook = f"{unique_value} {primary_keyword.title()} that helps you achieve more.\n\n"
        sections.append(hook)

        # Features (with keywords naturally integrated)
        features = app_info.get('key_features', [])
        if features:
            sections.append("KEY FEATURES:\n")
            for i, feature in enumerate(features[:5], 1):
                # Integrate keywords naturally
                feature_text = f"• {feature}"
                if i <= len(target_keywords):
                    keyword = target_keywords[i-1]
                    if keyword.lower() not in feature.lower():
                        feature_text = f"• {feature} with {keyword}"
                sections.append(f"{feature_text}\n")
            sections.append("\n")

        # Benefits
        target_audience = app_info.get('target_audience', 'users')
        sections.append(f"PERFECT FOR:\n{target_audience}\n\n")

        # Social proof placeholder
        sections.append("WHY USERS LOVE US:\n")
        sections.append("Join thousands of satisfied users who have transformed their workflow.\n\n")

        # CTA
        sections.append("Download now and start experiencing the difference!")

        # Combine and validate length
        full_description = "".join(sections)
        if len(full_description) > max_length:
            full_description = full_description[:max_length-3] + "..."

        # Calculate keyword density
        density = self.calculate_keyword_density(full_description, target_keywords)

        return {
            'full_description': full_description,
            'length': len(full_description),
            'remaining_chars': max_length - len(full_description),
            'keyword_analysis': density,
            'structure': {
                'has_hook': True,
                'has_features': len(features) > 0,
                'has_benefits': True,
                'has_cta': True
            }
        }
