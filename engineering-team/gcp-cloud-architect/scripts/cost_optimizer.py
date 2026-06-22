# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from cost_optimizer_base import *  # noqa: F403,E402
from cost_optimizer_p0 import main  # noqa: F401,E501
from cost_optimizer_c0 import CostOptimizerMixin0  # noqa: F401
from cost_optimizer_c1 import CostOptimizerMixin1  # noqa: F401
from cost_optimizer_c2 import CostOptimizerMixin2  # noqa: F401
from cost_optimizer_c3 import CostOptimizerMixin3  # noqa: F401
from cost_optimizer_c4 import CostOptimizerMixin4  # noqa: F401


class CostOptimizer(CostOptimizerMixin0, CostOptimizerMixin1, CostOptimizerMixin2, CostOptimizerMixin3, CostOptimizerMixin4):
    pass


if __name__ == '__main__':
    main()
