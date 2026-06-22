# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from inference_optimizer_base import *  # noqa: F403,E402
from inference_optimizer_p0 import main  # noqa: F401,E501
from inference_optimizer_c0 import InferenceOptimizerMixin0  # noqa: F401
from inference_optimizer_c1 import InferenceOptimizerMixin1  # noqa: F401
from inference_optimizer_c2 import InferenceOptimizerMixin2  # noqa: F401
from inference_optimizer_c3 import InferenceOptimizerMixin3  # noqa: F401
from inference_optimizer_c4 import InferenceOptimizerMixin4  # noqa: F401


class InferenceOptimizer(InferenceOptimizerMixin0, InferenceOptimizerMixin1, InferenceOptimizerMixin2, InferenceOptimizerMixin3, InferenceOptimizerMixin4):
    pass


if __name__ == '__main__':
    main()
