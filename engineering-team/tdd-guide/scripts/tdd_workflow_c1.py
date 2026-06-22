# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from tdd_workflow_base import *  # noqa: F403,E402
from tdd_workflow_p0 import TDDPhase, WorkflowState  # noqa: F401,E501


class TDDWorkflowMixin1:
    def validate_green_phase(
        self,
        implementation_code: str,
        test_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate GREEN phase completion.

        Args:
            implementation_code: The implementation code
            test_result: Test execution result

        Returns:
            Validation result and next steps
        """
        validations = []

        # Check implementation exists
        if not implementation_code or len(implementation_code.strip()) < 5:
            validations.append({
                'valid': False,
                'message': 'No implementation code provided'
            })
        else:
            validations.append({
                'valid': True,
                'message': 'Implementation code provided'
            })

        # Check test now passes
        test_passed = test_result.get('status') == 'passed'
        validations.append({
            'valid': test_passed,
            'message': 'Test passes' if test_passed else 'Test still failing'
        })

        # Check for minimal implementation (heuristic)
        is_minimal = self._check_minimal_implementation(implementation_code)
        validations.append({
            'valid': is_minimal,
            'message': 'Implementation appears minimal' if is_minimal
                      else 'Implementation may be over-engineered'
        })

        all_valid = all(v['valid'] for v in validations)

        if all_valid:
            self.state = WorkflowState.TEST_PASSING
            self.current_phase = TDDPhase.REFACTOR
            return {
                'phase_complete': True,
                'next_phase': 'REFACTOR',
                'validations': validations,
                'instruction': 'Refactor code while keeping tests green',
                'refactoring_suggestions': self._suggest_refactorings(implementation_code)
            }
        else:
            return {
                'phase_complete': False,
                'current_phase': 'GREEN',
                'validations': validations,
                'instruction': 'Make the test pass before refactoring'
            }
