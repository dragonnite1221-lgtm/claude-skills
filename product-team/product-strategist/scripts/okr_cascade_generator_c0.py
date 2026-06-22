# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from okr_cascade_generator_base import *  # noqa: F403,E402


class OKRGeneratorMixin0:
    """Generate and cascade OKRs across the organization"""
    def __init__(self, teams: List[str] = None, product_contribution: float = 0.3):
        """
        Initialize OKR generator.

        Args:
            teams: List of team names (default: Growth, Platform, Mobile, Data)
            product_contribution: Fraction of company KRs that product owns (default: 0.3)
        """
        self.teams = teams or ['Growth', 'Platform', 'Mobile', 'Data']
        self.product_contribution = product_contribution

        self.okr_templates = {
            'growth': {
                'objectives': [
                    'Accelerate user acquisition and market expansion',
                    'Achieve product-market fit in new segments',
                    'Build sustainable growth engine'
                ],
                'key_results': [
                    'Increase MAU from {current} to {target}',
                    'Achieve {target}% MoM growth rate',
                    'Expand to {target} new markets',
                    'Reduce CAC by {target}%',
                    'Improve activation rate to {target}%'
                ]
            },
            'retention': {
                'objectives': [
                    'Create lasting customer value and loyalty',
                    'Deliver a superior user experience',
                    'Maximize customer lifetime value'
                ],
                'key_results': [
                    'Improve retention from {current}% to {target}%',
                    'Increase NPS from {current} to {target}',
                    'Reduce churn to below {target}%',
                    'Achieve {target}% product stickiness',
                    'Increase LTV/CAC ratio to {target}'
                ]
            },
            'revenue': {
                'objectives': [
                    'Drive sustainable revenue growth',
                    'Optimize monetization strategy',
                    'Expand revenue per customer'
                ],
                'key_results': [
                    'Grow ARR from ${current}M to ${target}M',
                    'Increase ARPU by {target}%',
                    'Launch {target} new revenue streams',
                    'Achieve {target}% gross margin',
                    'Reduce revenue churn to {target}%'
                ]
            },
            'innovation': {
                'objectives': [
                    'Lead the market through product innovation',
                    'Establish leadership in key capability areas',
                    'Build sustainable competitive differentiation'
                ],
                'key_results': [
                    'Launch {target} breakthrough features',
                    'Achieve {target}% of revenue from new products',
                    'File {target} patents/IP',
                    'Reduce time-to-market by {target}%',
                    'Achieve {target} innovation score'
                ]
            },
            'operational': {
                'objectives': [
                    'Improve organizational efficiency',
                    'Achieve operational excellence',
                    'Scale operations sustainably'
                ],
                'key_results': [
                    'Improve velocity by {target}%',
                    'Reduce cycle time to {target} days',
                    'Achieve {target}% automation',
                    'Improve team satisfaction to {target}',
                    'Reduce incidents by {target}%'
                ]
            }
        }

        # Team focus areas for objective relevance matching
        self.team_relevance = {
            'Growth': ['acquisition', 'growth', 'activation', 'viral', 'onboarding', 'conversion'],
            'Platform': ['infrastructure', 'reliability', 'scale', 'performance', 'efficiency', 'automation'],
            'Mobile': ['mobile', 'app', 'ios', 'android', 'native'],
            'Data': ['analytics', 'metrics', 'insights', 'data', 'measurement', 'experimentation'],
            'Engineering': ['delivery', 'velocity', 'quality', 'automation', 'infrastructure'],
            'Design': ['experience', 'usability', 'interface', 'user', 'accessibility'],
            'Product': ['features', 'roadmap', 'prioritization', 'strategy'],
        }
