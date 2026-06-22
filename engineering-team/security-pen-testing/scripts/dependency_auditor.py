# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from dependency_auditor_base import *  # noqa: F403,E402
from dependency_auditor_p0 import Dependency, RiskyPattern, VulnerabilityFinding, format_report_text  # noqa: F401,E501
from dependency_auditor_p1 import main  # noqa: F401,E501
from dependency_auditor_c0 import DependencyAuditorMixin0  # noqa: F401
from dependency_auditor_c1 import DependencyAuditorMixin1  # noqa: F401


class DependencyAuditor(DependencyAuditorMixin0, DependencyAuditorMixin1):
    pass


if __name__ == "__main__":
    main()
