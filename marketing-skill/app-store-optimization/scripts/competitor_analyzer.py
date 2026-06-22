# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from competitor_analyzer_base import *  # noqa: F403,E402
from competitor_analyzer_p0 import analyze_competitor_set  # noqa: F401,E501
from competitor_analyzer_c0 import CompetitorAnalyzerMixin0  # noqa: F401
from competitor_analyzer_c1 import CompetitorAnalyzerMixin1  # noqa: F401
from competitor_analyzer_c2 import CompetitorAnalyzerMixin2  # noqa: F401
from competitor_analyzer_c3 import CompetitorAnalyzerMixin3  # noqa: F401
from competitor_analyzer_c4 import CompetitorAnalyzerMixin4  # noqa: F401
from competitor_analyzer_c5 import CompetitorAnalyzerMixin5  # noqa: F401


class CompetitorAnalyzer(CompetitorAnalyzerMixin0, CompetitorAnalyzerMixin1, CompetitorAnalyzerMixin2, CompetitorAnalyzerMixin3, CompetitorAnalyzerMixin4, CompetitorAnalyzerMixin5):
    pass
