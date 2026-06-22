# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from spec_validator_base import *  # noqa: F403,E402
from spec_validator_p0 import format_human, main  # noqa: F401,E501
from spec_validator_c0 import SpecValidatorMixin0  # noqa: F401
from spec_validator_c1 import SpecValidatorMixin1  # noqa: F401
from spec_validator_c2 import SpecValidatorMixin2  # noqa: F401


class SpecValidator(SpecValidatorMixin0, SpecValidatorMixin1, SpecValidatorMixin2):
    pass


if __name__ == "__main__":
    main()
