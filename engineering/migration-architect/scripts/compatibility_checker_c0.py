# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from compatibility_checker_base import *  # noqa: F403,E402


class SchemaCompatibilityCheckerMixin0:
    """Main schema compatibility checker class"""
    def __init__(self):
        self.type_compatibility_matrix = self._build_type_compatibility_matrix()
        self.constraint_implications = self._build_constraint_implications()
    def _build_type_compatibility_matrix(self) -> Dict[str, Dict[str, str]]:
        """Build data type compatibility matrix"""
        return {
            # SQL data types compatibility
            "varchar": {
                "text": "compatible",
                "char": "potentially_breaking",  # length might be different
                "nvarchar": "compatible",
                "int": "breaking",
                "bigint": "breaking",
                "decimal": "breaking",
                "datetime": "breaking",
                "boolean": "breaking"
            },
            "int": {
                "bigint": "compatible",
                "smallint": "potentially_breaking",  # range reduction
                "decimal": "compatible",
                "float": "potentially_breaking",  # precision loss
                "varchar": "breaking",
                "boolean": "breaking"
            },
            "bigint": {
                "int": "potentially_breaking",  # range reduction
                "decimal": "compatible",
                "varchar": "breaking",
                "boolean": "breaking"
            },
            "decimal": {
                "float": "potentially_breaking",  # precision loss
                "int": "potentially_breaking",  # precision loss
                "bigint": "potentially_breaking",  # precision loss
                "varchar": "breaking",
                "boolean": "breaking"
            },
            "datetime": {
                "timestamp": "compatible",
                "date": "potentially_breaking",  # time component lost
                "varchar": "breaking",
                "int": "breaking"
            },
            "boolean": {
                "tinyint": "compatible",
                "varchar": "breaking",
                "int": "breaking"
            },
            # JSON/API field types
            "string": {
                "number": "breaking",
                "boolean": "breaking",
                "array": "breaking",
                "object": "breaking",
                "null": "potentially_breaking"
            },
            "number": {
                "string": "breaking",
                "boolean": "breaking",
                "array": "breaking",
                "object": "breaking",
                "null": "potentially_breaking"
            },
            "boolean": {
                "string": "breaking",
                "number": "breaking",
                "array": "breaking",
                "object": "breaking",
                "null": "potentially_breaking"
            },
            "array": {
                "string": "breaking",
                "number": "breaking",
                "boolean": "breaking",
                "object": "breaking",
                "null": "potentially_breaking"
            },
            "object": {
                "string": "breaking",
                "number": "breaking",
                "boolean": "breaking",
                "array": "breaking",
                "null": "potentially_breaking"
            }
        }
