# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from api_linter_base import *  # noqa: F403,E402
from api_linter_p0 import LintIssue, LintReport  # noqa: F401,E501
from api_linter_p1 import main  # noqa: F401,E501
from api_linter_c0 import APILinterMixin0  # noqa: F401
from api_linter_c1 import APILinterMixin1  # noqa: F401
from api_linter_c2 import APILinterMixin2  # noqa: F401
from api_linter_c3 import APILinterMixin3  # noqa: F401
from api_linter_c4 import APILinterMixin4  # noqa: F401
from api_linter_c5 import APILinterMixin5  # noqa: F401
from api_linter_c6 import APILinterMixin6  # noqa: F401
from api_linter_c7 import APILinterMixin7  # noqa: F401


class APILinter(APILinterMixin0, APILinterMixin1, APILinterMixin2, APILinterMixin3, APILinterMixin4, APILinterMixin5, APILinterMixin6, APILinterMixin7):
    pass


if __name__ == '__main__':
    sys.exit(main())