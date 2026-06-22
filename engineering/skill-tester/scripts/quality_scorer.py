# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from quality_scorer_base import *  # noqa: F403,E402
from quality_scorer_p0 import QualityDimension  # noqa: F401,E501
from quality_scorer_p1 import QualityReport  # noqa: F401,E501
from quality_scorer_p2 import QualityReportFormatter  # noqa: F401,E501
from quality_scorer_p3 import main  # noqa: F401,E501
from quality_scorer_c0 import QualityScorerMixin0  # noqa: F401
from quality_scorer_c1 import QualityScorerMixin1  # noqa: F401
from quality_scorer_c2 import QualityScorerMixin2  # noqa: F401
from quality_scorer_c3 import QualityScorerMixin3  # noqa: F401
from quality_scorer_c4 import QualityScorerMixin4  # noqa: F401
from quality_scorer_c5 import QualityScorerMixin5  # noqa: F401
from quality_scorer_c6 import QualityScorerMixin6  # noqa: F401
from quality_scorer_c7 import QualityScorerMixin7  # noqa: F401
from quality_scorer_c8 import QualityScorerMixin8  # noqa: F401


class QualityScorer(QualityScorerMixin0, QualityScorerMixin1, QualityScorerMixin2, QualityScorerMixin3, QualityScorerMixin4, QualityScorerMixin5, QualityScorerMixin6, QualityScorerMixin7, QualityScorerMixin8):
    pass


if __name__ == "__main__":
    main()