# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from index_optimizer_base import *  # noqa: F403,E402
from index_optimizer_p0 import Column, Index, IndexRecommendation, QueryPattern, RedundancyIssue  # noqa: F401,E501
from index_optimizer_p1 import SelectivityEstimator  # noqa: F401,E501
from index_optimizer_p2 import main  # noqa: F401,E501
from index_optimizer_c0 import IndexOptimizerMixin0  # noqa: F401
from index_optimizer_c1 import IndexOptimizerMixin1  # noqa: F401
from index_optimizer_c2 import IndexOptimizerMixin2  # noqa: F401
from index_optimizer_c3 import IndexOptimizerMixin3  # noqa: F401
from index_optimizer_c4 import IndexOptimizerMixin4  # noqa: F401
from index_optimizer_c5 import IndexOptimizerMixin5  # noqa: F401
from index_optimizer_c6 import IndexOptimizerMixin6  # noqa: F401
from index_optimizer_c7 import IndexOptimizerMixin7  # noqa: F401


class IndexOptimizer(IndexOptimizerMixin0, IndexOptimizerMixin1, IndexOptimizerMixin2, IndexOptimizerMixin3, IndexOptimizerMixin4, IndexOptimizerMixin5, IndexOptimizerMixin6, IndexOptimizerMixin7):
    pass


if __name__ == "__main__":
    sys.exit(main())