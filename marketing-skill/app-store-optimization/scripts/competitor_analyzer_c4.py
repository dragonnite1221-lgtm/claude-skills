# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from competitor_analyzer_base import *  # noqa: F403,E402


class CompetitorAnalyzerMixin4:
    def _extract_features(self, description: str) -> List[str]:
        """Extract feature mentions from description."""
        # Look for bullet points or numbered lists
        lines = description.split('\n')
        features = []

        for line in lines:
            line = line.strip()
            # Check if line starts with bullet or number
            if line and (line[0] in ['•', '*', '-', '✓'] or line[0].isdigit()):
                # Clean the line
                cleaned = re.sub(r'^[•*\-✓\d.)\s]+', '', line)
                if cleaned:
                    features.append(cleaned)

        return features[:10]
    def _assess_keyword_focus(
        self,
        title_keywords: List[str],
        description_keywords: List[str]
    ) -> str:
        """Assess keyword focus strategy."""
        overlap = set(title_keywords) & set(description_keywords)

        if len(overlap) >= 3:
            return 'consistent_focus'
        elif len(overlap) >= 1:
            return 'moderate_focus'
        else:
            return 'broad_focus'
    def _generate_keyword_recommendations(self, missing_keywords: set) -> List[str]:
        """Generate recommendations for missing keywords."""
        if not missing_keywords:
            return ["Your keyword coverage is comprehensive"]

        recommendations = []
        missing_list = list(missing_keywords)[:5]

        recommendations.append(
            f"Consider adding these competitor keywords: {', '.join(missing_list)}"
        )
        recommendations.append(
            "Test keyword variations in subtitle/promotional text first"
        )
        recommendations.append(
            "Monitor competitor keyword changes monthly"
        )

        return recommendations
    def _generate_rating_improvement_actions(self, rating_gap: float) -> List[str]:
        """Generate actions to improve ratings."""
        actions = []

        if rating_gap > 0.5:
            actions.append("CRITICAL: Significant rating gap - prioritize user satisfaction improvements")
            actions.append("Analyze negative reviews to identify top issues")
            actions.append("Implement in-app rating prompts after positive experiences")
            actions.append("Respond to all negative reviews professionally")
        elif rating_gap > 0.2:
            actions.append("Focus on incremental improvements to close rating gap")
            actions.append("Optimize timing of rating requests")
        else:
            actions.append("Ratings are competitive - maintain quality and continue improvements")

        return actions
    def _generate_content_recommendations(self, desc_length_gap: int) -> List[str]:
        """Generate content recommendations based on length gap."""
        recommendations = []

        if desc_length_gap > 500:
            recommendations.append(
                "Expand description to match competitor detail level"
            )
            recommendations.append(
                "Add use case examples and success stories"
            )
            recommendations.append(
                "Include more feature explanations and benefits"
            )
        elif desc_length_gap < -500:
            recommendations.append(
                "Consider condensing description for better readability"
            )
            recommendations.append(
                "Focus on most important features first"
            )
        else:
            recommendations.append(
                "Description length is competitive"
            )

        return recommendations
