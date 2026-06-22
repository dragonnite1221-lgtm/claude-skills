# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from api_scorecard_base import *  # noqa: F403,E402
from api_scorecard_p0 import APIScorecard, CategoryScore, ScoreCategory  # noqa: F401,E501
from api_scorecard_p1 import main  # noqa: F401,E501
from api_scorecard_c0 import APIScoringEngineMixin0  # noqa: F401
from api_scorecard_c1 import APIScoringEngineMixin1  # noqa: F401
from api_scorecard_c2 import APIScoringEngineMixin2  # noqa: F401
from api_scorecard_c3 import APIScoringEngineMixin3  # noqa: F401
from api_scorecard_c4 import APIScoringEngineMixin4  # noqa: F401
from api_scorecard_c5 import APIScoringEngineMixin5  # noqa: F401
from api_scorecard_c6 import APIScoringEngineMixin6  # noqa: F401
from api_scorecard_c7 import APIScoringEngineMixin7  # noqa: F401
from api_scorecard_c8 import APIScoringEngineMixin8  # noqa: F401
from api_scorecard_c9 import APIScoringEngineMixin9  # noqa: F401
from api_scorecard_c10 import APIScoringEngineMixin10  # noqa: F401
from api_scorecard_c11 import APIScoringEngineMixin11  # noqa: F401
from api_scorecard_c12 import APIScoringEngineMixin12  # noqa: F401
from api_scorecard_c13 import APIScoringEngineMixin13  # noqa: F401
from api_scorecard_c14 import APIScoringEngineMixin14  # noqa: F401
from api_scorecard_c15 import APIScoringEngineMixin15  # noqa: F401


class APIScoringEngine(APIScoringEngineMixin0, APIScoringEngineMixin1, APIScoringEngineMixin2, APIScoringEngineMixin3, APIScoringEngineMixin4, APIScoringEngineMixin5, APIScoringEngineMixin6, APIScoringEngineMixin7, APIScoringEngineMixin8, APIScoringEngineMixin9, APIScoringEngineMixin10, APIScoringEngineMixin11, APIScoringEngineMixin12, APIScoringEngineMixin13, APIScoringEngineMixin14, APIScoringEngineMixin15):
    pass


if __name__ == '__main__':
    sys.exit(main())