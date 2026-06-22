# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from outlier_detector_base import *  # noqa: F403,E402
from outlier_detector_p2 import main  # noqa: F401


if __name__ == "__main__":
    main()
