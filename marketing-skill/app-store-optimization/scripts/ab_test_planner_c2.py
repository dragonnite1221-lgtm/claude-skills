# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from ab_test_planner_base import *  # noqa: F403,E402


class ABTestPlannerMixin2:
    def track_test_results(
        self,
        test_id: str,
        results_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Track ongoing test results and provide recommendations.

        Args:
            test_id: Test identifier
            results_data: Current test results

        Returns:
            Test tracking report with next steps
        """
        # Find test
        test = next((t for t in self.active_tests if t['test_id'] == test_id), None)
        if not test:
            return {'error': f'Test {test_id} not found'}

        # Calculate significance
        significance = self.calculate_significance(
            results_data['variant_a_conversions'],
            results_data['variant_a_visitors'],
            results_data['variant_b_conversions'],
            results_data['variant_b_visitors']
        )

        # Calculate test progress
        total_visitors = results_data['variant_a_visitors'] + results_data['variant_b_visitors']
        required_sample = results_data.get('required_sample_size', 10000)
        progress_percentage = min((total_visitors / required_sample) * 100, 100)

        # Generate recommendations
        recommendations = self._generate_tracking_recommendations(
            significance,
            progress_percentage,
            test['test_type']
        )

        return {
            'test_id': test_id,
            'test_type': test['test_type'],
            'progress': {
                'total_visitors': total_visitors,
                'required_sample_size': required_sample,
                'progress_percentage': round(progress_percentage, 1),
                'is_complete': progress_percentage >= 100
            },
            'current_results': significance,
            'recommendations': recommendations,
            'next_steps': self._determine_next_steps(
                significance,
                progress_percentage
            )
        }
    def generate_test_report(
        self,
        test_id: str,
        final_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate final test report with insights and recommendations.

        Args:
            test_id: Test identifier
            final_results: Final test results

        Returns:
            Comprehensive test report
        """
        test = next((t for t in self.active_tests if t['test_id'] == test_id), None)
        if not test:
            return {'error': f'Test {test_id} not found'}

        significance = self.calculate_significance(
            final_results['variant_a_conversions'],
            final_results['variant_a_visitors'],
            final_results['variant_b_conversions'],
            final_results['variant_b_visitors']
        )

        # Generate insights
        insights = self._generate_test_insights(
            test,
            significance,
            final_results
        )

        # Implementation plan
        implementation_plan = self._create_implementation_plan(
            test,
            significance
        )

        return {
            'test_summary': {
                'test_id': test_id,
                'test_type': test['test_type'],
                'hypothesis': test['hypothesis'],
                'duration_days': final_results.get('duration_days', 'N/A')
            },
            'results': significance,
            'insights': insights,
            'implementation_plan': implementation_plan,
            'learnings': self._extract_learnings(test, significance)
        }
