# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from tdd_workflow_base import *  # noqa: F403,E402
from tdd_workflow_p0 import TDDPhase, WorkflowState  # noqa: F401,E501


class TDDWorkflowMixin0:
    """Guide users through TDD red-green-refactor workflow."""
    def __init__(self):
        """Initialize TDD workflow guide."""
        self.current_phase = TDDPhase.RED
        self.state = WorkflowState.INITIAL
        self.history = []
    def start_cycle(self, requirement: str) -> Dict[str, Any]:
        """
        Start a new TDD cycle.

        Args:
            requirement: User story or requirement to implement

        Returns:
            Guidance for RED phase
        """
        self.current_phase = TDDPhase.RED
        self.state = WorkflowState.INITIAL

        return {
            'phase': 'RED',
            'instruction': 'Write a failing test for the requirement',
            'requirement': requirement,
            'checklist': [
                'Write test that describes desired behavior',
                'Test should fail when run (no implementation yet)',
                'Test name clearly describes what is being tested',
                'Test has clear arrange-act-assert structure'
            ],
            'tips': [
                'Focus on behavior, not implementation',
                'Start with simplest test case',
                'Test should be specific and focused'
            ]
        }
    def validate_red_phase(
        self,
        test_code: str,
        test_result: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Validate RED phase completion.

        Args:
            test_code: The test code written
            test_result: Test execution result (optional)

        Returns:
            Validation result and next steps
        """
        validations = []

        # Check test exists
        if not test_code or len(test_code.strip()) < 10:
            validations.append({
                'valid': False,
                'message': 'No test code provided'
            })
        else:
            validations.append({
                'valid': True,
                'message': 'Test code provided'
            })

        # Check for assertions
        has_assertion = any(keyword in test_code.lower()
                           for keyword in ['assert', 'expect', 'should'])
        validations.append({
            'valid': has_assertion,
            'message': 'Contains assertions' if has_assertion else 'Missing assertions'
        })

        # Check test result if provided
        if test_result:
            test_failed = test_result.get('status') == 'failed'
            validations.append({
                'valid': test_failed,
                'message': 'Test fails as expected' if test_failed else 'Test should fail in RED phase'
            })

        all_valid = all(v['valid'] for v in validations)

        if all_valid:
            self.state = WorkflowState.TEST_FAILING
            self.current_phase = TDDPhase.GREEN
            return {
                'phase_complete': True,
                'next_phase': 'GREEN',
                'validations': validations,
                'instruction': 'Write minimal code to make the test pass'
            }
        else:
            return {
                'phase_complete': False,
                'current_phase': 'RED',
                'validations': validations,
                'instruction': 'Address validation issues before proceeding'
            }
