# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from _test_generator_base import *  # noqa: F403,E402


class TestFramework(Enum):
    """Supported testing frameworks."""
    JEST = "jest"
    VITEST = "vitest"
    PYTEST = "pytest"
    JUNIT = "junit"
    MOCHA = "mocha"


class TestType(Enum):
    """Types of tests to generate."""
    UNIT = "unit"
    INTEGRATION = "integration"
    E2E = "e2e"
