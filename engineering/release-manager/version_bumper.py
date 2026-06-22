# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from version_bumper_base import *  # noqa: F403,E402
from version_bumper_p0 import BumpType, PreReleaseType  # noqa: F401,E501
from version_bumper_p1 import Version  # noqa: F401,E501
from version_bumper_p2 import ConventionalCommit  # noqa: F401,E501
from version_bumper_p3 import _cscd_0  # noqa: F401,E501
from version_bumper_p4 import main  # noqa: F401,E501
from version_bumper_c0 import VersionBumperMixin0  # noqa: F401
from version_bumper_c1 import VersionBumperMixin1  # noqa: F401
from version_bumper_c2 import VersionBumperMixin2  # noqa: F401


class VersionBumper(VersionBumperMixin0, VersionBumperMixin1, VersionBumperMixin2):
    pass


if __name__ == '__main__':
    main()