# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from coverage_analyzer_base import *  # noqa: F403,E402
from coverage_analyzer_p0 import CoverageFormat  # noqa: F401,E501
from coverage_analyzer_c0 import CoverageAnalyzerMixin0  # noqa: F401
from coverage_analyzer_c1 import CoverageAnalyzerMixin1  # noqa: F401
from coverage_analyzer_c2 import CoverageAnalyzerMixin2  # noqa: F401
from coverage_analyzer_c3 import CoverageAnalyzerMixin3  # noqa: F401
from coverage_analyzer_c4 import CoverageAnalyzerMixin4  # noqa: F401


class CoverageAnalyzer(CoverageAnalyzerMixin0, CoverageAnalyzerMixin1, CoverageAnalyzerMixin2, CoverageAnalyzerMixin3, CoverageAnalyzerMixin4):
    pass
