# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from skill_validator_base import *  # noqa: F403,E402
from skill_validator_p0 import ValidationError, ValidationReport  # noqa: F401,E501
from skill_validator_p1 import ReportFormatter  # noqa: F401,E501
from skill_validator_p2 import main  # noqa: F401,E501
from skill_validator_c0 import SkillValidatorMixin0  # noqa: F401
from skill_validator_c1 import SkillValidatorMixin1  # noqa: F401
from skill_validator_c2 import SkillValidatorMixin2  # noqa: F401
from skill_validator_c3 import SkillValidatorMixin3  # noqa: F401


class SkillValidator(SkillValidatorMixin0, SkillValidatorMixin1, SkillValidatorMixin2, SkillValidatorMixin3):
    pass


if __name__ == "__main__":
    main()
