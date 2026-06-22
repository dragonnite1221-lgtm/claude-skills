# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from pir_generator_base import *  # noqa: F403,E402
from pir_generator_p0 import format_json_output, format_markdown_output, format_text_output  # noqa: F401,E501
from pir_generator_p1 import main  # noqa: F401,E501
from pir_generator_c0 import PIRGeneratorMixin0  # noqa: F401
from pir_generator_c1 import PIRGeneratorMixin1  # noqa: F401
from pir_generator_c2 import PIRGeneratorMixin2  # noqa: F401
from pir_generator_c3 import PIRGeneratorMixin3  # noqa: F401
from pir_generator_c4 import PIRGeneratorMixin4  # noqa: F401
from pir_generator_c5 import PIRGeneratorMixin5  # noqa: F401
from pir_generator_c6 import PIRGeneratorMixin6  # noqa: F401
from pir_generator_c7 import PIRGeneratorMixin7  # noqa: F401
from pir_generator_c8 import PIRGeneratorMixin8  # noqa: F401
from pir_generator_c9 import PIRGeneratorMixin9  # noqa: F401
from pir_generator_c10 import PIRGeneratorMixin10  # noqa: F401
from pir_generator_c11 import PIRGeneratorMixin11  # noqa: F401
from pir_generator_c12 import PIRGeneratorMixin12  # noqa: F401
from pir_generator_c13 import PIRGeneratorMixin13  # noqa: F401
from pir_generator_c14 import PIRGeneratorMixin14  # noqa: F401


class PIRGenerator(PIRGeneratorMixin0, PIRGeneratorMixin1, PIRGeneratorMixin2, PIRGeneratorMixin3, PIRGeneratorMixin4, PIRGeneratorMixin5, PIRGeneratorMixin6, PIRGeneratorMixin7, PIRGeneratorMixin8, PIRGeneratorMixin9, PIRGeneratorMixin10, PIRGeneratorMixin11, PIRGeneratorMixin12, PIRGeneratorMixin13, PIRGeneratorMixin14):
    pass


if __name__ == "__main__":
    main()