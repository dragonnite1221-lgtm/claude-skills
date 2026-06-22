# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from breaking_change_detector_base import *  # noqa: F403,E402
from breaking_change_detector_p0 import Change, ChangeSeverity, ChangeType, ComparisonReport  # noqa: F401,E501
from breaking_change_detector_p1 import main  # noqa: F401,E501
from breaking_change_detector_c0 import BreakingChangeDetectorMixin0  # noqa: F401
from breaking_change_detector_c1 import BreakingChangeDetectorMixin1  # noqa: F401
from breaking_change_detector_c2 import BreakingChangeDetectorMixin2  # noqa: F401
from breaking_change_detector_c3 import BreakingChangeDetectorMixin3  # noqa: F401
from breaking_change_detector_c4 import BreakingChangeDetectorMixin4  # noqa: F401
from breaking_change_detector_c5 import BreakingChangeDetectorMixin5  # noqa: F401
from breaking_change_detector_c6 import BreakingChangeDetectorMixin6  # noqa: F401
from breaking_change_detector_c7 import BreakingChangeDetectorMixin7  # noqa: F401
from breaking_change_detector_c8 import BreakingChangeDetectorMixin8  # noqa: F401
from breaking_change_detector_c9 import BreakingChangeDetectorMixin9  # noqa: F401


class BreakingChangeDetector(BreakingChangeDetectorMixin0, BreakingChangeDetectorMixin1, BreakingChangeDetectorMixin2, BreakingChangeDetectorMixin3, BreakingChangeDetectorMixin4, BreakingChangeDetectorMixin5, BreakingChangeDetectorMixin6, BreakingChangeDetectorMixin7, BreakingChangeDetectorMixin8, BreakingChangeDetectorMixin9):
    pass


if __name__ == '__main__':
    sys.exit(main())