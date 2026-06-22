# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from api_load_tester_base import *  # noqa: F403,E402
from api_load_tester_p5 import main  # noqa: F401


if __name__ == '__main__':
    main()
