# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from data_subject_rights_tracker_base import *  # noqa: F403,E402
from data_subject_rights_tracker_p0 import main  # noqa: F401,E501
from data_subject_rights_tracker_c0 import RightsTrackerMixin0  # noqa: F401
from data_subject_rights_tracker_c1 import RightsTrackerMixin1  # noqa: F401
from data_subject_rights_tracker_c2 import RightsTrackerMixin2  # noqa: F401


class RightsTracker(RightsTrackerMixin0, RightsTrackerMixin1, RightsTrackerMixin2):
    pass


if __name__ == "__main__":
    main()
