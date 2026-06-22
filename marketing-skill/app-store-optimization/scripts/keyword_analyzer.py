# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from keyword_analyzer_base import *  # noqa: F403,E402
from keyword_analyzer_p0 import analyze_keyword_set  # noqa: F401,E501
from keyword_analyzer_c0 import KeywordAnalyzerMixin0  # noqa: F401
from keyword_analyzer_c1 import KeywordAnalyzerMixin1  # noqa: F401
from keyword_analyzer_c2 import KeywordAnalyzerMixin2  # noqa: F401
from keyword_analyzer_c3 import KeywordAnalyzerMixin3  # noqa: F401


class KeywordAnalyzer(KeywordAnalyzerMixin0, KeywordAnalyzerMixin1, KeywordAnalyzerMixin2, KeywordAnalyzerMixin3):
    pass
