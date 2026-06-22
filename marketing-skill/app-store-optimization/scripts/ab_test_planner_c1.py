# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from ab_test_planner_base import *  # noqa: F403,E402


class ABTestPlannerMixin1:
    def calculate_significance(
        self,
        variant_a_conversions: int,
        variant_a_visitors: int,
        variant_b_conversions: int,
        variant_b_visitors: int
    ) -> Dict[str, Any]:
        """
        Calculate statistical significance of test results.

        Args:
            variant_a_conversions: Conversions for control
            variant_a_visitors: Visitors for control
            variant_b_conversions: Conversions for variation
            variant_b_visitors: Visitors for variation

        Returns:
            Significance analysis with decision recommendation
        """
        # Calculate conversion rates
        rate_a = variant_a_conversions / variant_a_visitors if variant_a_visitors > 0 else 0
        rate_b = variant_b_conversions / variant_b_visitors if variant_b_visitors > 0 else 0

        # Calculate improvement
        if rate_a > 0:
            relative_improvement = (rate_b - rate_a) / rate_a
        else:
            relative_improvement = 0

        absolute_improvement = rate_b - rate_a

        # Calculate standard error
        se_a = math.sqrt(rate_a * (1 - rate_a) / variant_a_visitors) if variant_a_visitors > 0 else 0
        se_b = math.sqrt(rate_b * (1 - rate_b) / variant_b_visitors) if variant_b_visitors > 0 else 0
        se_diff = math.sqrt(se_a**2 + se_b**2)

        # Calculate z-score
        z_score = absolute_improvement / se_diff if se_diff > 0 else 0

        # Calculate p-value (two-tailed)
        p_value = 2 * (1 - self._standard_normal_cdf(abs(z_score)))

        # Determine significance
        is_significant_95 = p_value < 0.05
        is_significant_90 = p_value < 0.10

        # Generate decision
        decision = self._generate_test_decision(
            relative_improvement,
            is_significant_95,
            is_significant_90,
            variant_a_visitors + variant_b_visitors
        )

        return {
            'variant_a': {
                'conversions': variant_a_conversions,
                'visitors': variant_a_visitors,
                'conversion_rate': round(rate_a, 4)
            },
            'variant_b': {
                'conversions': variant_b_conversions,
                'visitors': variant_b_visitors,
                'conversion_rate': round(rate_b, 4)
            },
            'improvement': {
                'absolute': round(absolute_improvement, 4),
                'relative_percentage': round(relative_improvement * 100, 2)
            },
            'statistical_analysis': {
                'z_score': round(z_score, 3),
                'p_value': round(p_value, 4),
                'is_significant_95': is_significant_95,
                'is_significant_90': is_significant_90,
                'confidence_level': '95%' if is_significant_95 else ('90%' if is_significant_90 else 'Not significant')
            },
            'decision': decision
        }
