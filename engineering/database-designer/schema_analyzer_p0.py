# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from schema_analyzer_base import *  # noqa: F403,E402


@dataclass
class Column:
    name: str
    data_type: str
    nullable: bool = True
    primary_key: bool = False
    unique: bool = False
    foreign_key: Optional[str] = None
    default_value: Optional[str] = None
    check_constraint: Optional[str] = None


@dataclass
class Index:
    name: str
    table: str
    columns: List[str]
    unique: bool = False
    index_type: str = "btree"


@dataclass
class Table:
    name: str
    columns: List[Column]
    primary_key: List[str]
    foreign_keys: List[Tuple[str, str]]  # (column, referenced_table.column)
    unique_constraints: List[List[str]]
    check_constraints: Dict[str, str]
    indexes: List[Index]


@dataclass
class NormalizationIssue:
    table: str
    issue_type: str
    severity: str
    description: str
    suggestion: str
    columns_affected: List[str]


@dataclass
class DataTypeIssue:
    table: str
    column: str
    current_type: str
    issue: str
    suggested_type: str
    rationale: str


@dataclass
class ConstraintIssue:
    table: str
    issue_type: str
    severity: str
    description: str
    suggestion: str
    columns_affected: List[str]


@dataclass
class NamingIssue:
    table: str
    column: Optional[str]
    issue: str
    current_name: str
    suggested_name: str
