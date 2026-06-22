# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from coverage_analyzer_base import *  # noqa: F403,E402


class CoverageFormat:
    """Supported coverage report formats."""
    LCOV = "lcov"
    JSON = "json"
    XML = "xml"
    COBERTURA = "cobertura"
