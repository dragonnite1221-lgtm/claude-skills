# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from dependency_analyzer_base import *  # noqa: F403,E402
from dependency_analyzer_p0 import print_human_report  # noqa: F401,E501
from dependency_analyzer_p1 import main  # noqa: F401,E501
from dependency_analyzer_c0 import DependencyAnalyzerMixin0  # noqa: F401
from dependency_analyzer_c1 import DependencyAnalyzerMixin1  # noqa: F401
from dependency_analyzer_c2 import DependencyAnalyzerMixin2  # noqa: F401
from dependency_analyzer_c3 import DependencyAnalyzerMixin3  # noqa: F401
from dependency_analyzer_c4 import DependencyAnalyzerMixin4  # noqa: F401


class DependencyAnalyzer(DependencyAnalyzerMixin0, DependencyAnalyzerMixin1, DependencyAnalyzerMixin2, DependencyAnalyzerMixin3, DependencyAnalyzerMixin4):
    pass


if __name__ == '__main__':
    main()
