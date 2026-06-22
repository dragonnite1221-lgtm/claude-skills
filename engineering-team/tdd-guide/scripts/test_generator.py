# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from _test_generator_base import *  # noqa: F403,E402
from _test_generator_p0 import TestFramework, TestType  # noqa: F401,E501
from _test_generator_c0 import _TestGeneratorMixin0  # noqa: F401
from _test_generator_c1 import _TestGeneratorMixin1  # noqa: F401
from _test_generator_c2 import _TestGeneratorMixin2  # noqa: F401
from _test_generator_c3 import _TestGeneratorMixin3  # noqa: F401


class TestGenerator(_TestGeneratorMixin0, _TestGeneratorMixin1, _TestGeneratorMixin2, _TestGeneratorMixin3):
    pass
