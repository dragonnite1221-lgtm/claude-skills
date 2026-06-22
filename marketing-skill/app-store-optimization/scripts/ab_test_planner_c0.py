# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from ab_test_planner_base import *  # noqa: F403,E402


class ABTestPlannerMixin0:
    """Plans and tracks A/B tests for ASO elements."""
    MIN_EFFECT_SIZES = {
        'icon': 0.10,  # 10% conversion improvement
        'screenshot': 0.08,  # 8% conversion improvement
        'title': 0.05,  # 5% conversion improvement
        'description': 0.03  # 3% conversion improvement
    }
    CONFIDENCE_LEVELS = {
        'high': 0.95,  # 95% confidence
        'standard': 0.90,  # 90% confidence
        'exploratory': 0.80  # 80% confidence
    }
    def __init__(self):
        """Initialize A/B test planner."""
        self.active_tests = []
    def design_test(
        self,
        test_type: str,
        variant_a: Dict[str, Any],
        variant_b: Dict[str, Any],
        hypothesis: str,
        success_metric: str = 'conversion_rate'
    ) -> Dict[str, Any]:
        """
        Design an A/B test with hypothesis and variables.

        Args:
            test_type: Type of test ('icon', 'screenshot', 'title', 'description')
            variant_a: Control variant details
            variant_b: Test variant details
            hypothesis: Expected outcome hypothesis
            success_metric: Metric to optimize

        Returns:
            Test design with configuration
        """
        test_design = {
            'test_id': self._generate_test_id(test_type),
            'test_type': test_type,
            'hypothesis': hypothesis,
            'variants': {
                'a': {
                    'name': 'Control',
                    'details': variant_a,
                    'traffic_split': 0.5
                },
                'b': {
                    'name': 'Variation',
                    'details': variant_b,
                    'traffic_split': 0.5
                }
            },
            'success_metric': success_metric,
            'secondary_metrics': self._get_secondary_metrics(test_type),
            'minimum_effect_size': self.MIN_EFFECT_SIZES.get(test_type, 0.05),
            'recommended_confidence': 'standard',
            'best_practices': self._get_test_best_practices(test_type)
        }

        self.active_tests.append(test_design)
        return test_design
    def calculate_sample_size(
        self,
        baseline_conversion: float,
        minimum_detectable_effect: float,
        confidence_level: str = 'standard',
        power: float = 0.80
    ) -> Dict[str, Any]:
        """
        Calculate required sample size for statistical significance.

        Args:
            baseline_conversion: Current conversion rate (0-1)
            minimum_detectable_effect: Minimum effect size to detect (0-1)
            confidence_level: 'high', 'standard', or 'exploratory'
            power: Statistical power (typically 0.80 or 0.90)

        Returns:
            Sample size calculation with duration estimates
        """
        alpha = 1 - self.CONFIDENCE_LEVELS[confidence_level]
        beta = 1 - power

        # Expected conversion for variant B
        expected_conversion_b = baseline_conversion * (1 + minimum_detectable_effect)

        # Z-scores for alpha and beta
        z_alpha = self._get_z_score(1 - alpha / 2)  # Two-tailed test
        z_beta = self._get_z_score(power)

        # Pooled standard deviation
        p_pooled = (baseline_conversion + expected_conversion_b) / 2
        sd_pooled = math.sqrt(2 * p_pooled * (1 - p_pooled))

        # Sample size per variant
        n_per_variant = math.ceil(
            ((z_alpha + z_beta) ** 2 * sd_pooled ** 2) /
            ((expected_conversion_b - baseline_conversion) ** 2)
        )

        total_sample_size = n_per_variant * 2

        # Estimate duration based on typical traffic
        duration_estimates = self._estimate_test_duration(
            total_sample_size,
            baseline_conversion
        )

        return {
            'sample_size_per_variant': n_per_variant,
            'total_sample_size': total_sample_size,
            'baseline_conversion': baseline_conversion,
            'expected_conversion_improvement': minimum_detectable_effect,
            'expected_conversion_b': expected_conversion_b,
            'confidence_level': confidence_level,
            'statistical_power': power,
            'duration_estimates': duration_estimates,
            'recommendations': self._generate_sample_size_recommendations(
                n_per_variant,
                duration_estimates
            )
        }
