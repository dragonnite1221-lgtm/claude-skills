# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from upgrade_planner_base import *  # noqa: F403,E402
from upgrade_planner_p0 import DependencyUpgrade, UpdateType, UpgradePlan, UpgradeRisk, VersionInfo  # noqa: F401,E501
from upgrade_planner_p1 import main  # noqa: F401,E501
from upgrade_planner_c0 import UpgradePlannerMixin0  # noqa: F401
from upgrade_planner_c1 import UpgradePlannerMixin1  # noqa: F401
from upgrade_planner_c2 import UpgradePlannerMixin2  # noqa: F401
from upgrade_planner_c3 import UpgradePlannerMixin3  # noqa: F401
from upgrade_planner_c4 import UpgradePlannerMixin4  # noqa: F401
from upgrade_planner_c5 import UpgradePlannerMixin5  # noqa: F401
from upgrade_planner_c6 import UpgradePlannerMixin6  # noqa: F401
from upgrade_planner_c7 import UpgradePlannerMixin7  # noqa: F401
from upgrade_planner_c8 import UpgradePlannerMixin8  # noqa: F401


class UpgradePlanner(UpgradePlannerMixin0, UpgradePlannerMixin1, UpgradePlannerMixin2, UpgradePlannerMixin3, UpgradePlannerMixin4, UpgradePlannerMixin5, UpgradePlannerMixin6, UpgradePlannerMixin7, UpgradePlannerMixin8):
    pass


if __name__ == '__main__':
    main()