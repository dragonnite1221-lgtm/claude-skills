# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from compatibility_checker_base import *  # noqa: F403,E402
from compatibility_checker_p0 import ChangeType, CompatibilityIssue, CompatibilityLevel, CompatibilityReport, MigrationScript  # noqa: F401,E501
from compatibility_checker_p1 import main  # noqa: F401,E501
from compatibility_checker_c0 import SchemaCompatibilityCheckerMixin0  # noqa: F401
from compatibility_checker_c1 import SchemaCompatibilityCheckerMixin1  # noqa: F401
from compatibility_checker_c2 import SchemaCompatibilityCheckerMixin2  # noqa: F401
from compatibility_checker_c3 import SchemaCompatibilityCheckerMixin3  # noqa: F401
from compatibility_checker_c4 import SchemaCompatibilityCheckerMixin4  # noqa: F401
from compatibility_checker_c5 import SchemaCompatibilityCheckerMixin5  # noqa: F401
from compatibility_checker_c6 import SchemaCompatibilityCheckerMixin6  # noqa: F401
from compatibility_checker_c7 import SchemaCompatibilityCheckerMixin7  # noqa: F401
from compatibility_checker_c8 import SchemaCompatibilityCheckerMixin8  # noqa: F401
from compatibility_checker_c9 import SchemaCompatibilityCheckerMixin9  # noqa: F401


class SchemaCompatibilityChecker(SchemaCompatibilityCheckerMixin0, SchemaCompatibilityCheckerMixin1, SchemaCompatibilityCheckerMixin2, SchemaCompatibilityCheckerMixin3, SchemaCompatibilityCheckerMixin4, SchemaCompatibilityCheckerMixin5, SchemaCompatibilityCheckerMixin6, SchemaCompatibilityCheckerMixin7, SchemaCompatibilityCheckerMixin8, SchemaCompatibilityCheckerMixin9):
    pass


if __name__ == "__main__":
    sys.exit(main())