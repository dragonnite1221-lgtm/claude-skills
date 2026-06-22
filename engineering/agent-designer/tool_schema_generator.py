# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from tool_schema_generator_base import *  # noqa: F403,E402
from tool_schema_generator_p0 import ErrorSpec, ParameterSpec, ParameterType, RateLimitSpec, ToolDescription, ToolSchema, ValidationRule  # noqa: F401,E501
from tool_schema_generator_p1 import main  # noqa: F401,E501
from tool_schema_generator_c0 import ToolSchemaGeneratorMixin0  # noqa: F401
from tool_schema_generator_c1 import ToolSchemaGeneratorMixin1  # noqa: F401
from tool_schema_generator_c2 import ToolSchemaGeneratorMixin2  # noqa: F401
from tool_schema_generator_c3 import ToolSchemaGeneratorMixin3  # noqa: F401
from tool_schema_generator_c4 import ToolSchemaGeneratorMixin4  # noqa: F401
from tool_schema_generator_c5 import ToolSchemaGeneratorMixin5  # noqa: F401
from tool_schema_generator_c6 import ToolSchemaGeneratorMixin6  # noqa: F401
from tool_schema_generator_c7 import ToolSchemaGeneratorMixin7  # noqa: F401


class ToolSchemaGenerator(ToolSchemaGeneratorMixin0, ToolSchemaGeneratorMixin1, ToolSchemaGeneratorMixin2, ToolSchemaGeneratorMixin3, ToolSchemaGeneratorMixin4, ToolSchemaGeneratorMixin5, ToolSchemaGeneratorMixin6, ToolSchemaGeneratorMixin7):
    pass


if __name__ == "__main__":
    main()