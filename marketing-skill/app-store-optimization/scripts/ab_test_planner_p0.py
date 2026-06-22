# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from ab_test_planner_base import *  # noqa: F403,E402


def plan_ab_test(
    test_type: str,
    variant_a: Dict[str, Any],
    variant_b: Dict[str, Any],
    hypothesis: str,
    baseline_conversion: float
) -> Dict[str, Any]:
    """
    Convenience function to plan an A/B test.

    Args:
        test_type: Type of test
        variant_a: Control variant
        variant_b: Test variant
        hypothesis: Test hypothesis
        baseline_conversion: Current conversion rate

    Returns:
        Complete test plan
    """
    planner = ABTestPlanner()

    test_design = planner.design_test(
        test_type,
        variant_a,
        variant_b,
        hypothesis
    )

    sample_size = planner.calculate_sample_size(
        baseline_conversion,
        planner.MIN_EFFECT_SIZES.get(test_type, 0.05)
    )

    return {
        'test_design': test_design,
        'sample_size_requirements': sample_size
    }
