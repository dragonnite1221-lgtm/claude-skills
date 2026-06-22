# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from project_architect_base import *  # noqa: F403,E402
from project_architect_p0 import PatternDetector  # noqa: F401,E501
from project_architect_p1 import LayerViolationDetector  # noqa: F401,E501
from project_architect_p2 import ProjectArchitect  # noqa: F401,E501
from project_architect_p3 import print_human_report  # noqa: F401,E501
from project_architect_p4 import main  # noqa: F401,E501
from project_architect_c0 import CodeAnalyzerMixin0  # noqa: F401
from project_architect_c1 import CodeAnalyzerMixin1  # noqa: F401


class CodeAnalyzer(CodeAnalyzerMixin0, CodeAnalyzerMixin1):
    pass


if __name__ == '__main__':
    main()
