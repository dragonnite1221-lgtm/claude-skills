# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from dep_scanner_base import *  # noqa: F403,E402
from dep_scanner_p0 import Dependency, Vulnerability, main  # noqa: F401,E501
from dep_scanner_c0 import DependencyScannerMixin0  # noqa: F401
from dep_scanner_c1 import DependencyScannerMixin1  # noqa: F401
from dep_scanner_c2 import DependencyScannerMixin2  # noqa: F401
from dep_scanner_c3 import DependencyScannerMixin3  # noqa: F401
from dep_scanner_c4 import DependencyScannerMixin4  # noqa: F401
from dep_scanner_c5 import DependencyScannerMixin5  # noqa: F401
from dep_scanner_c6 import DependencyScannerMixin6  # noqa: F401


class DependencyScanner(DependencyScannerMixin0, DependencyScannerMixin1, DependencyScannerMixin2, DependencyScannerMixin3, DependencyScannerMixin4, DependencyScannerMixin5, DependencyScannerMixin6):
    pass


if __name__ == '__main__':
    main()