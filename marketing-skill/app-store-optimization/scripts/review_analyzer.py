# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from review_analyzer_base import *  # noqa: F403,E402
from review_analyzer_p0 import analyze_reviews  # noqa: F401,E501
from review_analyzer_c0 import ReviewAnalyzerMixin0  # noqa: F401
from review_analyzer_c1 import ReviewAnalyzerMixin1  # noqa: F401
from review_analyzer_c2 import ReviewAnalyzerMixin2  # noqa: F401
from review_analyzer_c3 import ReviewAnalyzerMixin3  # noqa: F401
from review_analyzer_c4 import ReviewAnalyzerMixin4  # noqa: F401
from review_analyzer_c5 import ReviewAnalyzerMixin5  # noqa: F401
from review_analyzer_c6 import ReviewAnalyzerMixin6  # noqa: F401
from review_analyzer_c7 import ReviewAnalyzerMixin7  # noqa: F401


class ReviewAnalyzer(ReviewAnalyzerMixin0, ReviewAnalyzerMixin1, ReviewAnalyzerMixin2, ReviewAnalyzerMixin3, ReviewAnalyzerMixin4, ReviewAnalyzerMixin5, ReviewAnalyzerMixin6, ReviewAnalyzerMixin7):
    pass
