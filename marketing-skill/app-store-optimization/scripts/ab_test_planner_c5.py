# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from ab_test_planner_base import *  # noqa: F403,E402


class ABTestPlannerMixin5:
    def _generate_test_insights(
        self,
        test: Dict[str, Any],
        significance: Dict[str, Any],
        results: Dict[str, Any]
    ) -> List[str]:
        """Generate insights from test results."""
        insights = []

        improvement = significance['improvement']['relative_percentage']

        if significance['statistical_analysis']['is_significant_95']:
            insights.append(
                f"Strong evidence: Variant B {'improved' if improvement > 0 else 'decreased'} "
                f"conversion by {abs(improvement):.1f}% with 95% confidence"
            )

        insights.append(
            f"Tested {test['test_type']} changes: {test['hypothesis']}"
        )

        # Add context-specific insights
        if test['test_type'] == 'icon' and improvement > 5:
            insights.append(
                "Icon change had substantial impact - visual first impression is critical"
            )

        return insights
    def _create_implementation_plan(
        self,
        test: Dict[str, Any],
        significance: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Create implementation plan for winning variant."""
        plan = []

        if significance.get('decision', {}).get('decision') == 'implement_b':
            plan.append({
                'step': '1. Update store listing',
                'details': f"Replace {test['test_type']} with Variant B across all platforms"
            })
            plan.append({
                'step': '2. Monitor metrics',
                'details': 'Track conversion rate for 2 weeks to confirm sustained improvement'
            })
            plan.append({
                'step': '3. Document learnings',
                'details': 'Record insights for future optimization'
            })

        return plan
    def _extract_learnings(
        self,
        test: Dict[str, Any],
        significance: Dict[str, Any]
    ) -> List[str]:
        """Extract key learnings from test."""
        learnings = []

        improvement = significance['improvement']['relative_percentage']

        learnings.append(
            f"Testing {test['test_type']} can yield {abs(improvement):.1f}% conversion change"
        )

        if test['test_type'] == 'title':
            learnings.append(
                "Title changes affect search visibility and user perception"
            )
        elif test['test_type'] == 'screenshot':
            learnings.append(
                "First 2-3 screenshots are critical for conversion"
            )

        return learnings
