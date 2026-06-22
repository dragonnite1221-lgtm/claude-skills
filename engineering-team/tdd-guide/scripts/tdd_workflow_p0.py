# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from tdd_workflow_base import *  # noqa: F403,E402


class TDDPhase(Enum):
    """TDD cycle phases."""
    RED = "red"  # Write failing test
    GREEN = "green"  # Make test pass
    REFACTOR = "refactor"  # Improve code


class WorkflowState(Enum):
    """Current state of TDD workflow."""
    INITIAL = "initial"
    TEST_WRITTEN = "test_written"
    TEST_FAILING = "test_failing"
    TEST_PASSING = "test_passing"
    CODE_REFACTORED = "code_refactored"
