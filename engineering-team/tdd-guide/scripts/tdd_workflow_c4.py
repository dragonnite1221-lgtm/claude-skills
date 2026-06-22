# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from tdd_workflow_base import *  # noqa: F403,E402
from tdd_workflow_p0 import TDDPhase  # noqa: F401,E501


class TDDWorkflowMixin4:
    def get_phase_guidance(self, phase: Optional[TDDPhase] = None) -> Dict[str, Any]:
        """
        Get detailed guidance for a specific phase.

        Args:
            phase: TDD phase (uses current if not specified)

        Returns:
            Detailed guidance dictionary
        """
        target_phase = phase or self.current_phase

        if target_phase == TDDPhase.RED:
            return {
                'phase': 'RED',
                'goal': 'Write a failing test',
                'steps': [
                    '1. Read and understand the requirement',
                    '2. Think about expected behavior',
                    '3. Write test that verifies this behavior',
                    '4. Run test and ensure it fails',
                    '5. Verify failure reason is correct (not syntax error)'
                ],
                'common_mistakes': [
                    'Test passes immediately (no real assertion)',
                    'Test fails for wrong reason (syntax error)',
                    'Test is too broad or tests multiple things'
                ],
                'tips': [
                    'Start with simplest test case',
                    'One assertion per test (focused)',
                    'Test should read like specification'
                ]
            }

        elif target_phase == TDDPhase.GREEN:
            return {
                'phase': 'GREEN',
                'goal': 'Make the test pass with minimal code',
                'steps': [
                    '1. Write simplest code that makes test pass',
                    '2. Run test and verify it passes',
                    '3. Run all tests to ensure no regression',
                    '4. Resist urge to add extra features'
                ],
                'common_mistakes': [
                    'Over-engineering solution',
                    'Adding features not covered by tests',
                    'Breaking existing tests'
                ],
                'tips': [
                    'Fake it till you make it (hardcode if needed)',
                    'Triangulate with more tests if needed',
                    'Keep implementation simple'
                ]
            }

        elif target_phase == TDDPhase.REFACTOR:
            return {
                'phase': 'REFACTOR',
                'goal': 'Improve code quality while keeping tests green',
                'steps': [
                    '1. Identify code smells or duplication',
                    '2. Apply one refactoring at a time',
                    '3. Run tests after each change',
                    '4. Commit when satisfied with quality'
                ],
                'common_mistakes': [
                    'Changing behavior (breaking tests)',
                    'Refactoring too much at once',
                    'Skipping this phase'
                ],
                'tips': [
                    'Extract methods for better naming',
                    'Remove duplication',
                    'Improve variable names',
                    'Tests are safety net - use them!'
                ]
            }

        return {}
