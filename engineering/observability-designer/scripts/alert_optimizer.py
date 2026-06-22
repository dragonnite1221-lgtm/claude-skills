# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from alert_optimizer_base import *  # noqa: F403,E402
from alert_optimizer_p0 import main  # noqa: F401,E501
from alert_optimizer_c0 import AlertOptimizerMixin0  # noqa: F401
from alert_optimizer_c1 import AlertOptimizerMixin1  # noqa: F401
from alert_optimizer_c2 import AlertOptimizerMixin2  # noqa: F401
from alert_optimizer_c3 import AlertOptimizerMixin3  # noqa: F401
from alert_optimizer_c4 import AlertOptimizerMixin4  # noqa: F401
from alert_optimizer_c5 import AlertOptimizerMixin5  # noqa: F401
from alert_optimizer_c6 import AlertOptimizerMixin6  # noqa: F401
from alert_optimizer_c7 import AlertOptimizerMixin7  # noqa: F401
from alert_optimizer_c8 import AlertOptimizerMixin8  # noqa: F401
from alert_optimizer_c9 import AlertOptimizerMixin9  # noqa: F401


class AlertOptimizer(AlertOptimizerMixin0, AlertOptimizerMixin1, AlertOptimizerMixin2, AlertOptimizerMixin3, AlertOptimizerMixin4, AlertOptimizerMixin5, AlertOptimizerMixin6, AlertOptimizerMixin7, AlertOptimizerMixin8, AlertOptimizerMixin9):
    pass


if __name__ == '__main__':
    main()