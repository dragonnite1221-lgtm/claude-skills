# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from cost_optimizer_base import *  # noqa: F403,E402
from cost_optimizer_p0 import _format_text, main  # noqa: F401,E501
from cost_optimizer_c0 import AzureCostOptimizerMixin0  # noqa: F401
from cost_optimizer_c1 import AzureCostOptimizerMixin1  # noqa: F401
from cost_optimizer_c2 import AzureCostOptimizerMixin2  # noqa: F401
from cost_optimizer_c3 import AzureCostOptimizerMixin3  # noqa: F401


class AzureCostOptimizer(AzureCostOptimizerMixin0, AzureCostOptimizerMixin1, AzureCostOptimizerMixin2, AzureCostOptimizerMixin3):
    pass


if __name__ == "__main__":
    main()
