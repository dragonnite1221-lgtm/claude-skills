# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from compliance_checker_base import *  # noqa: F403,E402
from compliance_checker_p0 import ComplianceControl, main  # noqa: F401,E501
from compliance_checker_c0 import ComplianceCheckerMixin0  # noqa: F401
from compliance_checker_c1 import ComplianceCheckerMixin1  # noqa: F401
from compliance_checker_c2 import ComplianceCheckerMixin2  # noqa: F401
from compliance_checker_c3 import ComplianceCheckerMixin3  # noqa: F401
from compliance_checker_c4 import ComplianceCheckerMixin4  # noqa: F401
from compliance_checker_c5 import ComplianceCheckerMixin5  # noqa: F401
from compliance_checker_c6 import ComplianceCheckerMixin6  # noqa: F401
from compliance_checker_c7 import ComplianceCheckerMixin7  # noqa: F401
from compliance_checker_c8 import ComplianceCheckerMixin8  # noqa: F401
from compliance_checker_c9 import ComplianceCheckerMixin9  # noqa: F401
from compliance_checker_c10 import ComplianceCheckerMixin10  # noqa: F401


class ComplianceChecker(ComplianceCheckerMixin0, ComplianceCheckerMixin1, ComplianceCheckerMixin2, ComplianceCheckerMixin3, ComplianceCheckerMixin4, ComplianceCheckerMixin5, ComplianceCheckerMixin6, ComplianceCheckerMixin7, ComplianceCheckerMixin8, ComplianceCheckerMixin9, ComplianceCheckerMixin10):
    pass


if __name__ == "__main__":
    main()
