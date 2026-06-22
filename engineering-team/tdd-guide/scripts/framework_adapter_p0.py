# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from framework_adapter_base import *  # noqa: F403,E402


class Framework(Enum):
    """Supported testing frameworks."""
    JEST = "jest"
    VITEST = "vitest"
    PYTEST = "pytest"
    UNITTEST = "unittest"
    JUNIT = "junit"
    TESTNG = "testng"
    MOCHA = "mocha"
    JASMINE = "jasmine"


class Language(Enum):
    """Supported programming languages."""
    TYPESCRIPT = "typescript"
    JAVASCRIPT = "javascript"
    PYTHON = "python"
    JAVA = "java"
