# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from design_token_generator_base import *  # noqa: F403,E402
from design_token_generator_p0 import main  # noqa: F401,E501
from design_token_generator_c0 import DesignTokenGeneratorMixin0  # noqa: F401
from design_token_generator_c1 import DesignTokenGeneratorMixin1  # noqa: F401
from design_token_generator_c2 import DesignTokenGeneratorMixin2  # noqa: F401
from design_token_generator_c3 import DesignTokenGeneratorMixin3  # noqa: F401
from design_token_generator_c4 import DesignTokenGeneratorMixin4  # noqa: F401


class DesignTokenGenerator(DesignTokenGeneratorMixin0, DesignTokenGeneratorMixin1, DesignTokenGeneratorMixin2, DesignTokenGeneratorMixin3, DesignTokenGeneratorMixin4):
    pass


if __name__ == "__main__":
    main()
