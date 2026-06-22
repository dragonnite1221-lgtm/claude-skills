# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from ab_test_planner_base import *  # noqa: F403,E402


class ABTestPlannerMixin3:
    def _generate_test_id(self, test_type: str) -> str:
        """Generate unique test ID."""
        import time
        timestamp = int(time.time())
        return f"{test_type}_{timestamp}"
    def _get_secondary_metrics(self, test_type: str) -> List[str]:
        """Get secondary metrics to track for test type."""
        metrics_map = {
            'icon': ['tap_through_rate', 'impression_count', 'brand_recall'],
            'screenshot': ['tap_through_rate', 'time_on_page', 'scroll_depth'],
            'title': ['impression_count', 'tap_through_rate', 'search_visibility'],
            'description': ['time_on_page', 'scroll_depth', 'tap_through_rate']
        }
        return metrics_map.get(test_type, ['tap_through_rate'])
    def _get_test_best_practices(self, test_type: str) -> List[str]:
        """Get best practices for specific test type."""
        practices_map = {
            'icon': [
                'Test only one element at a time (color vs. style vs. symbolism)',
                'Ensure icon is recognizable at small sizes (60x60px)',
                'Consider cultural context for global audience',
                'Test against top competitor icons'
            ],
            'screenshot': [
                'Test order of screenshots (users see first 2-3)',
                'Use captions to tell story',
                'Show key features and benefits',
                'Test with and without device frames'
            ],
            'title': [
                'Test keyword variations, not major rebrand',
                'Keep brand name consistent',
                'Ensure title fits within character limits',
                'Test on both search and browse contexts'
            ],
            'description': [
                'Test structure (bullet points vs. paragraphs)',
                'Test call-to-action placement',
                'Test feature vs. benefit focus',
                'Maintain keyword density'
            ]
        }
        return practices_map.get(test_type, ['Test one variable at a time'])
    def _estimate_test_duration(
        self,
        required_sample_size: int,
        baseline_conversion: float
    ) -> Dict[str, Any]:
        """Estimate test duration based on typical traffic levels."""
        # Assume different daily traffic scenarios
        traffic_scenarios = {
            'low': 100,      # 100 page views/day
            'medium': 1000,  # 1000 page views/day
            'high': 10000    # 10000 page views/day
        }

        estimates = {}
        for scenario, daily_views in traffic_scenarios.items():
            days = math.ceil(required_sample_size / daily_views)
            estimates[scenario] = {
                'daily_page_views': daily_views,
                'estimated_days': days,
                'estimated_weeks': round(days / 7, 1)
            }

        return estimates
    def _generate_sample_size_recommendations(
        self,
        sample_size: int,
        duration_estimates: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations based on sample size."""
        recommendations = []

        if sample_size > 50000:
            recommendations.append(
                "Large sample size required - consider testing smaller effect size or increasing traffic"
            )

        if duration_estimates['medium']['estimated_days'] > 30:
            recommendations.append(
                "Long test duration - consider higher minimum detectable effect or focus on high-impact changes"
            )

        if duration_estimates['low']['estimated_days'] > 60:
            recommendations.append(
                "Insufficient traffic for reliable testing - consider user acquisition or broader targeting"
            )

        if not recommendations:
            recommendations.append("Sample size and duration are reasonable for this test")

        return recommendations
    def _get_z_score(self, percentile: float) -> float:
        """Get z-score for given percentile (approximation)."""
        # Common z-scores
        z_scores = {
            0.80: 0.84,
            0.85: 1.04,
            0.90: 1.28,
            0.95: 1.645,
            0.975: 1.96,
            0.99: 2.33
        }
        return z_scores.get(percentile, 1.96)
