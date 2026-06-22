# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from tdd_workflow_base import *  # noqa: F403,E402
from tdd_workflow_p0 import WorkflowState  # noqa: F401,E501


class TDDWorkflowMixin2:
    def validate_refactor_phase(
        self,
        original_code: str,
        refactored_code: str,
        test_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate REFACTOR phase completion.

        Args:
            original_code: Original implementation
            refactored_code: Refactored implementation
            test_result: Test execution result after refactoring

        Returns:
            Validation result and cycle completion status
        """
        validations = []

        # Check tests still pass
        test_passed = test_result.get('status') == 'passed'
        validations.append({
            'valid': test_passed,
            'message': 'Tests still pass after refactoring' if test_passed
                      else 'Tests broken by refactoring'
        })

        # Check code was actually refactored
        code_changed = original_code != refactored_code
        validations.append({
            'valid': code_changed,
            'message': 'Code was refactored' if code_changed
                      else 'No refactoring applied (optional)'
        })

        # Check code quality improved
        quality_improved = self._check_quality_improvement(original_code, refactored_code)
        if code_changed:
            validations.append({
                'valid': quality_improved,
                'message': 'Code quality improved' if quality_improved
                          else 'Consider further refactoring for better quality'
            })

        all_valid = all(v['valid'] for v in validations if v.get('valid') is not None)

        if all_valid:
            self.state = WorkflowState.CODE_REFACTORED
            self.history.append({
                'cycle_complete': True,
                'final_state': self.state
            })
            return {
                'phase_complete': True,
                'cycle_complete': True,
                'validations': validations,
                'message': 'TDD cycle complete! Ready for next requirement.',
                'next_steps': [
                    'Commit your changes',
                    'Start next TDD cycle with new requirement',
                    'Or add more test cases for current feature'
                ]
            }
        else:
            return {
                'phase_complete': False,
                'current_phase': 'REFACTOR',
                'validations': validations,
                'instruction': 'Ensure tests still pass after refactoring'
            }
    def _check_minimal_implementation(self, code: str) -> bool:
        """Check if implementation is minimal (heuristic)."""
        # Simple heuristics:
        # - Not too long (< 50 lines for unit tests)
        # - Not too complex (few nested structures)

        lines = code.split('\n')
        non_empty_lines = [line for line in lines if line.strip() and not line.strip().startswith('#')]

        # Check length
        if len(non_empty_lines) > 50:
            return False

        # Check nesting depth (simplified)
        max_depth = 0
        current_depth = 0
        for line in lines:
            stripped = line.lstrip()
            if stripped:
                indent = len(line) - len(stripped)
                depth = indent // 4  # Assuming 4-space indent
                max_depth = max(max_depth, depth)

        # Max nesting of 3 levels for simple implementation
        return max_depth <= 3
