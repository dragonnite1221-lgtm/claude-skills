# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from index_optimizer_base import *  # noqa: F403,E402


@dataclass
class Column:
    name: str
    data_type: str
    nullable: bool = True
    unique: bool = False
    cardinality_estimate: Optional[int] = None


@dataclass
class Index:
    name: str
    table: str
    columns: List[str]
    unique: bool = False
    index_type: str = "btree"
    partial_condition: Optional[str] = None
    include_columns: List[str] = None
    size_estimate: Optional[int] = None


@dataclass
class QueryPattern:
    query_id: str
    query_type: str  # SELECT, INSERT, UPDATE, DELETE
    table: str
    where_conditions: List[Dict[str, Any]]
    join_conditions: List[Dict[str, Any]]
    order_by: List[Dict[str, str]]  # column, direction
    group_by: List[str]
    frequency: int = 1
    avg_execution_time_ms: Optional[float] = None


@dataclass
class IndexRecommendation:
    recommendation_id: str
    table: str
    recommended_index: Index
    reason: str
    query_patterns_helped: List[str]
    estimated_benefit: str
    estimated_overhead: str
    priority: int  # 1 = highest priority
    sql_statement: str
    selectivity_analysis: Dict[str, Any]


@dataclass
class RedundancyIssue:
    issue_type: str  # DUPLICATE, OVERLAPPING, UNUSED
    affected_indexes: List[str]
    table: str
    description: str
    recommendation: str
    sql_statements: List[str]
