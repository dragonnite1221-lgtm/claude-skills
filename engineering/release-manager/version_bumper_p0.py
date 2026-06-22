# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from version_bumper_base import *  # noqa: F403,E402


class BumpType(Enum):
    """Version bump types."""
    NONE = "none"
    PATCH = "patch"
    MINOR = "minor"  
    MAJOR = "major"


class PreReleaseType(Enum):
    """Pre-release types."""
    ALPHA = "alpha"
    BETA = "beta"
    RC = "rc"
