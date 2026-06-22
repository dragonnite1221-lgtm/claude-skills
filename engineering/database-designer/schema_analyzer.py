# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from schema_analyzer_base import *  # noqa: F403,E402
from schema_analyzer_p0 import Column, ConstraintIssue, DataTypeIssue, Index, NamingIssue, NormalizationIssue, Table  # noqa: F401,E501
from schema_analyzer_p1 import main  # noqa: F401,E501
from schema_analyzer_c0 import SchemaAnalyzerMixin0  # noqa: F401
from schema_analyzer_c1 import SchemaAnalyzerMixin1  # noqa: F401
from schema_analyzer_c2 import SchemaAnalyzerMixin2  # noqa: F401
from schema_analyzer_c3 import SchemaAnalyzerMixin3  # noqa: F401
from schema_analyzer_c4 import SchemaAnalyzerMixin4  # noqa: F401
from schema_analyzer_c5 import SchemaAnalyzerMixin5  # noqa: F401
from schema_analyzer_c6 import SchemaAnalyzerMixin6  # noqa: F401
from schema_analyzer_c7 import SchemaAnalyzerMixin7  # noqa: F401


class SchemaAnalyzer(SchemaAnalyzerMixin0, SchemaAnalyzerMixin1, SchemaAnalyzerMixin2, SchemaAnalyzerMixin3, SchemaAnalyzerMixin4, SchemaAnalyzerMixin5, SchemaAnalyzerMixin6, SchemaAnalyzerMixin7):
    pass


if __name__ == "__main__":
    sys.exit(main())