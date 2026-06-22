# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from vision_model_trainer_base import *  # noqa: F403,E402
from vision_model_trainer_p0 import main  # noqa: F401,E501
from vision_model_trainer_c0 import VisionModelTrainerMixin0  # noqa: F401
from vision_model_trainer_c1 import VisionModelTrainerMixin1  # noqa: F401
from vision_model_trainer_c2 import VisionModelTrainerMixin2  # noqa: F401
from vision_model_trainer_c3 import VisionModelTrainerMixin3  # noqa: F401
from vision_model_trainer_c4 import VisionModelTrainerMixin4  # noqa: F401


class VisionModelTrainer(VisionModelTrainerMixin0, VisionModelTrainerMixin1, VisionModelTrainerMixin2, VisionModelTrainerMixin3, VisionModelTrainerMixin4):
    pass


if __name__ == '__main__':
    main()
