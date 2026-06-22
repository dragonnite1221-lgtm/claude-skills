# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from debt_scanner_base import *  # noqa: F403,E402
from debt_scanner_p0 import PythonASTAnalyzer  # noqa: F401,E501
from debt_scanner_p1 import format_human_readable_report, main  # noqa: F401,E501
from debt_scanner_c0 import DebtScannerMixin0  # noqa: F401
from debt_scanner_c1 import DebtScannerMixin1  # noqa: F401
from debt_scanner_c2 import DebtScannerMixin2  # noqa: F401
from debt_scanner_c3 import DebtScannerMixin3  # noqa: F401


class DebtScanner(DebtScannerMixin0, DebtScannerMixin1, DebtScannerMixin2, DebtScannerMixin3):
    pass


if __name__ == "__main__":
    main()