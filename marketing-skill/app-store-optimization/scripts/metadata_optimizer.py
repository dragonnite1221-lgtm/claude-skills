# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from metadata_optimizer_base import *  # noqa: F403,E402
from metadata_optimizer_p0 import optimize_app_metadata  # noqa: F401,E501
from metadata_optimizer_c0 import MetadataOptimizerMixin0  # noqa: F401
from metadata_optimizer_c1 import MetadataOptimizerMixin1  # noqa: F401
from metadata_optimizer_c2 import MetadataOptimizerMixin2  # noqa: F401
from metadata_optimizer_c3 import MetadataOptimizerMixin3  # noqa: F401
from metadata_optimizer_c4 import MetadataOptimizerMixin4  # noqa: F401


class MetadataOptimizer(MetadataOptimizerMixin0, MetadataOptimizerMixin1, MetadataOptimizerMixin2, MetadataOptimizerMixin3, MetadataOptimizerMixin4):
    pass
