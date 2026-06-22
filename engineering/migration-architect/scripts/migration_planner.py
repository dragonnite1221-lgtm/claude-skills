# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from migration_planner_base import *  # noqa: F403,E402
from migration_planner_p0 import MigrationComplexity, MigrationConstraint, MigrationPhase, MigrationPlan, MigrationType, RiskItem, RiskLevel  # noqa: F401,E501
from migration_planner_p1 import main  # noqa: F401,E501
from migration_planner_c0 import MigrationPlannerMixin0  # noqa: F401
from migration_planner_c1 import MigrationPlannerMixin1  # noqa: F401
from migration_planner_c2 import MigrationPlannerMixin2  # noqa: F401
from migration_planner_c3 import MigrationPlannerMixin3  # noqa: F401
from migration_planner_c4 import MigrationPlannerMixin4  # noqa: F401
from migration_planner_c5 import MigrationPlannerMixin5  # noqa: F401


class MigrationPlanner(MigrationPlannerMixin0, MigrationPlannerMixin1, MigrationPlannerMixin2, MigrationPlannerMixin3, MigrationPlannerMixin4, MigrationPlannerMixin5):
    pass


if __name__ == "__main__":
    sys.exit(main())