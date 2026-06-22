# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from aso_scorer_base import *  # noqa: F403,E402
from aso_scorer_p0 import calculate_aso_score  # noqa: F401,E501
from aso_scorer_c0 import ASOScorerMixin0  # noqa: F401
from aso_scorer_c1 import ASOScorerMixin1  # noqa: F401
from aso_scorer_c2 import ASOScorerMixin2  # noqa: F401
from aso_scorer_c3 import ASOScorerMixin3  # noqa: F401
from aso_scorer_c4 import ASOScorerMixin4  # noqa: F401
from aso_scorer_c5 import ASOScorerMixin5  # noqa: F401


class ASOScorer(ASOScorerMixin0, ASOScorerMixin1, ASOScorerMixin2, ASOScorerMixin3, ASOScorerMixin4, ASOScorerMixin5):
    pass
