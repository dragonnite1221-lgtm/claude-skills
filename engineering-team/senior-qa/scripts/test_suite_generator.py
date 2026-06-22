# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from _test_suite_generator_base import *  # noqa: F403,E402
from _test_suite_generator_p0 import ComponentInfo, TestCase, TestFile  # noqa: F401,E501
from _test_suite_generator_p1 import ComponentScanner  # noqa: F401,E501
from _test_suite_generator_p2 import TestSuiteGenerator  # noqa: F401,E501
from _test_suite_generator_p3 import main  # noqa: F401,E501
from _test_suite_generator_c0 import _TestGeneratorMixin0  # noqa: F401
from _test_suite_generator_c1 import _TestGeneratorMixin1  # noqa: F401
from _test_suite_generator_c2 import _TestGeneratorMixin2  # noqa: F401


class TestGenerator(_TestGeneratorMixin0, _TestGeneratorMixin1, _TestGeneratorMixin2):
    pass


if __name__ == '__main__':
    main()
