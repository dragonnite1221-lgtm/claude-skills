# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from question_bank_generator_base import *  # noqa: F403,E402
from question_bank_generator_p0 import _mod_cg0_0  # noqa: F401,E501
from question_bank_generator_p1 import _mod_cg0_1  # noqa: F401,E501
from question_bank_generator_p2 import format_human_readable  # noqa: F401,E501
from question_bank_generator_p3 import main  # noqa: F401,E501
from question_bank_generator_c0 import QuestionBankGeneratorMixin0  # noqa: F401
from question_bank_generator_c1 import QuestionBankGeneratorMixin1  # noqa: F401
from question_bank_generator_c2 import QuestionBankGeneratorMixin2  # noqa: F401
from question_bank_generator_c3 import QuestionBankGeneratorMixin3  # noqa: F401
from question_bank_generator_c4 import QuestionBankGeneratorMixin4  # noqa: F401
from question_bank_generator_c5 import QuestionBankGeneratorMixin5  # noqa: F401
from question_bank_generator_c6 import QuestionBankGeneratorMixin6  # noqa: F401


class QuestionBankGenerator(QuestionBankGeneratorMixin0, QuestionBankGeneratorMixin1, QuestionBankGeneratorMixin2, QuestionBankGeneratorMixin3, QuestionBankGeneratorMixin4, QuestionBankGeneratorMixin5, QuestionBankGeneratorMixin6):
    pass


if __name__ == "__main__":
    main()