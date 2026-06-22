# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from aso_scorer_base import *  # noqa: F403,E402


class ASOScorerMixin4:
    def generate_recommendations(
        self,
        metadata_score: float,
        ratings_score: float,
        keyword_score: float,
        conversion_score: float
    ) -> List[Dict[str, Any]]:
        """Generate prioritized recommendations based on scores."""
        recommendations = []

        # Metadata recommendations
        if metadata_score < 60:
            recommendations.append({
                'category': 'metadata_quality',
                'priority': 'high',
                'action': 'Optimize app title and description',
                'details': 'Add more keywords to title, expand description to 1500-2000 characters, improve keyword density to 3-5%',
                'expected_impact': 'Improve discoverability and ranking potential'
            })
        elif metadata_score < 80:
            recommendations.append({
                'category': 'metadata_quality',
                'priority': 'medium',
                'action': 'Refine metadata for better keyword targeting',
                'details': 'Test variations of title/subtitle, optimize keyword field for Apple',
                'expected_impact': 'Incremental ranking improvements'
            })

        # Ratings recommendations
        if ratings_score < 60:
            recommendations.append({
                'category': 'ratings_reviews',
                'priority': 'high',
                'action': 'Improve rating quality and volume',
                'details': 'Address top user complaints, implement in-app rating prompts, respond to negative reviews',
                'expected_impact': 'Better conversion rates and trust signals'
            })
        elif ratings_score < 80:
            recommendations.append({
                'category': 'ratings_reviews',
                'priority': 'medium',
                'action': 'Increase rating velocity',
                'details': 'Optimize timing of rating requests, encourage satisfied users to rate',
                'expected_impact': 'Sustained rating quality'
            })

        # Keyword performance recommendations
        if keyword_score < 60:
            recommendations.append({
                'category': 'keyword_performance',
                'priority': 'high',
                'action': 'Improve keyword rankings',
                'details': 'Target long-tail keywords with lower competition, update metadata with high-potential keywords, build backlinks',
                'expected_impact': 'Significant improvement in organic visibility'
            })
        elif keyword_score < 80:
            recommendations.append({
                'category': 'keyword_performance',
                'priority': 'medium',
                'action': 'Expand keyword coverage',
                'details': 'Target additional related keywords, test seasonal keywords, localize for new markets',
                'expected_impact': 'Broader reach and more discovery opportunities'
            })

        # Conversion recommendations
        if conversion_score < 60:
            recommendations.append({
                'category': 'conversion_metrics',
                'priority': 'high',
                'action': 'Optimize store listing for conversions',
                'details': 'Improve screenshots and icon, strengthen value proposition in description, add video preview',
                'expected_impact': 'Higher impression-to-install conversion'
            })
        elif conversion_score < 80:
            recommendations.append({
                'category': 'conversion_metrics',
                'priority': 'medium',
                'action': 'Test visual asset variations',
                'details': 'A/B test different icon designs and screenshot sequences',
                'expected_impact': 'Incremental conversion improvements'
            })

        return recommendations
    def _assess_health_status(self, overall_score: float) -> str:
        """Assess overall ASO health status."""
        if overall_score >= 80:
            return "Excellent - Top-tier ASO performance"
        elif overall_score >= 65:
            return "Good - Competitive ASO with room for improvement"
        elif overall_score >= 50:
            return "Fair - Needs strategic improvements"
        else:
            return "Poor - Requires immediate ASO overhaul"
    def _prioritize_actions(
        self,
        recommendations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Prioritize actions by impact and urgency."""
        # Sort by priority (high first) and expected impact
        priority_order = {'high': 0, 'medium': 1, 'low': 2}

        sorted_recommendations = sorted(
            recommendations,
            key=lambda x: priority_order[x['priority']]
        )

        return sorted_recommendations[:3]  # Top 3 priority actions
