# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from metadata_optimizer_base import *  # noqa: F403,E402


class MetadataOptimizerMixin4:
    def _remove_plural_duplicates(self, keywords: List[str]) -> List[str]:
        """Remove plural forms if singular exists."""
        deduplicated = []
        singular_set = set()

        for keyword in keywords:
            if keyword.endswith('s') and len(keyword) > 1:
                singular = keyword[:-1]
                if singular not in singular_set:
                    deduplicated.append(singular)
                    singular_set.add(singular)
            else:
                if keyword not in singular_set:
                    deduplicated.append(keyword)
                    singular_set.add(keyword)

        return deduplicated
    def _build_keyword_field(self, keywords: List[str], max_length: int) -> str:
        """Build comma-separated keyword field within character limit."""
        keyword_field = ""

        for keyword in keywords:
            test_field = f"{keyword_field},{keyword}" if keyword_field else keyword
            if len(test_field) <= max_length:
                keyword_field = test_field
            else:
                break

        return keyword_field
    def _calculate_coverage(self, keywords: List[str], text: str) -> Dict[str, int]:
        """Calculate how many keywords are covered in text."""
        text_lower = text.lower()
        coverage = {}

        for keyword in keywords:
            coverage[keyword] = text_lower.count(keyword.lower())

        return coverage
    def _assess_density(self, density: float) -> str:
        """Assess individual keyword density."""
        if density < 0.5:
            return "too_low"
        elif density <= 2.5:
            return "optimal"
        else:
            return "too_high"
    def _assess_overall_density(self, density: float) -> str:
        """Assess overall keyword density."""
        if density < 2:
            return "Under-optimized: Consider adding more keyword variations"
        elif density <= 5:
            return "Optimal: Good keyword integration without stuffing"
        elif density <= 8:
            return "High: Approaching keyword stuffing - reduce keyword usage"
        else:
            return "Too High: Keyword stuffing detected - rewrite for natural flow"
    def _generate_density_recommendations(
        self,
        keyword_densities: Dict[str, Dict[str, Any]]
    ) -> List[str]:
        """Generate recommendations based on keyword density analysis."""
        recommendations = []

        for keyword, data in keyword_densities.items():
            if data['status'] == 'too_low':
                recommendations.append(
                    f"Increase usage of '{keyword}' - currently only {data['occurrences']} times"
                )
            elif data['status'] == 'too_high':
                recommendations.append(
                    f"Reduce usage of '{keyword}' - appears {data['occurrences']} times (keyword stuffing risk)"
                )

        if not recommendations:
            recommendations.append("Keyword density is well-balanced")

        return recommendations
    def _recommend_title_option(self, options: List[Dict[str, Any]]) -> str:
        """Recommend best title option based on strategy."""
        if not options:
            return "No valid options available"

        # Prefer brand_plus_primary for established apps
        for option in options:
            if option['strategy'] == 'brand_plus_primary':
                return f"Recommended: '{option['title']}' (Balance of brand and SEO)"

        # Fallback to first option
        return f"Recommended: '{options[0]['title']}' ({options[0]['strategy']})"
