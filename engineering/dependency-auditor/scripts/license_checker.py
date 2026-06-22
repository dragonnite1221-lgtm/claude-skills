# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from license_checker_base import *  # noqa: F403,E402
from license_checker_p0 import DependencyLicense, LicenseConflict, LicenseInfo, LicenseType, RiskLevel  # noqa: F401,E501
from license_checker_p1 import _mod_cg0_0  # noqa: F401,E501
from license_checker_p2 import _mod_cg0_1  # noqa: F401,E501
from license_checker_p3 import main  # noqa: F401,E501
from license_checker_c0 import LicenseCheckerMixin0  # noqa: F401
from license_checker_c1 import LicenseCheckerMixin1  # noqa: F401
from license_checker_c2 import LicenseCheckerMixin2  # noqa: F401
from license_checker_c3 import LicenseCheckerMixin3  # noqa: F401
from license_checker_c4 import LicenseCheckerMixin4  # noqa: F401
from license_checker_c5 import LicenseCheckerMixin5  # noqa: F401
from license_checker_c6 import LicenseCheckerMixin6  # noqa: F401
from license_checker_c7 import LicenseCheckerMixin7  # noqa: F401


class LicenseChecker(LicenseCheckerMixin0, LicenseCheckerMixin1, LicenseCheckerMixin2, LicenseCheckerMixin3, LicenseCheckerMixin4, LicenseCheckerMixin5, LicenseCheckerMixin6, LicenseCheckerMixin7):
    pass


if __name__ == '__main__':
    main()