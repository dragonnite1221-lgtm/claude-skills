# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from debt_dashboard_base import *  # noqa: F403,E402
from debt_dashboard_p0 import DebtVelocity, HealthMetrics, TrendAnalysis, format_dashboard_report  # noqa: F401,E501
from debt_dashboard_p1 import main  # noqa: F401,E501
from debt_dashboard_c0 import DebtDashboardMixin0  # noqa: F401
from debt_dashboard_c1 import DebtDashboardMixin1  # noqa: F401
from debt_dashboard_c2 import DebtDashboardMixin2  # noqa: F401
from debt_dashboard_c3 import DebtDashboardMixin3  # noqa: F401
from debt_dashboard_c4 import DebtDashboardMixin4  # noqa: F401
from debt_dashboard_c5 import DebtDashboardMixin5  # noqa: F401
from debt_dashboard_c6 import DebtDashboardMixin6  # noqa: F401
from debt_dashboard_c7 import DebtDashboardMixin7  # noqa: F401
from debt_dashboard_c8 import DebtDashboardMixin8  # noqa: F401


class DebtDashboard(DebtDashboardMixin0, DebtDashboardMixin1, DebtDashboardMixin2, DebtDashboardMixin3, DebtDashboardMixin4, DebtDashboardMixin5, DebtDashboardMixin6, DebtDashboardMixin7, DebtDashboardMixin8):
    pass


if __name__ == "__main__":
    main()