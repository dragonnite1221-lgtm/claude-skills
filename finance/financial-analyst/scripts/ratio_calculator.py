# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from ratio_calculator_base import *  # noqa: F403,E402
from ratio_calculator_p0 import main, safe_divide  # noqa: F401,E501
from ratio_calculator_c0 import FinancialRatioCalculatorMixin0  # noqa: F401
from ratio_calculator_c1 import FinancialRatioCalculatorMixin1  # noqa: F401
from ratio_calculator_c2 import FinancialRatioCalculatorMixin2  # noqa: F401
from ratio_calculator_c3 import FinancialRatioCalculatorMixin3  # noqa: F401


class FinancialRatioCalculator(FinancialRatioCalculatorMixin0, FinancialRatioCalculatorMixin1, FinancialRatioCalculatorMixin2, FinancialRatioCalculatorMixin3):
    pass


if __name__ == "__main__":
    main()
