# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from script_tester_base import *  # noqa: F403,E402
from script_tester_p0 import ScriptTestResult, TestError, TestSuite  # noqa: F401,E501
from script_tester_p1 import TestReportFormatter  # noqa: F401,E501
from script_tester_p2 import main  # noqa: F401,E501
from script_tester_c0 import ScriptTesterMixin0  # noqa: F401
from script_tester_c1 import ScriptTesterMixin1  # noqa: F401
from script_tester_c2 import ScriptTesterMixin2  # noqa: F401
from script_tester_c3 import ScriptTesterMixin3  # noqa: F401
from script_tester_c4 import ScriptTesterMixin4  # noqa: F401


class ScriptTester(ScriptTesterMixin0, ScriptTesterMixin1, ScriptTesterMixin2, ScriptTesterMixin3, ScriptTesterMixin4):
    pass


if __name__ == "__main__":
    main()