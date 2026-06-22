# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from data_quality_validator_base import *  # noqa: F403,E402


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


@dataclass
class ColumnSchema:
    """Schema definition for a column"""
    name: str
    data_type: str  # string, integer, float, boolean, date, datetime, email, uuid
    nullable: bool = True
    unique: bool = False
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    pattern: Optional[str] = None  # regex pattern
    allowed_values: Optional[List[str]] = None
    description: str = ""


@dataclass
class DataSchema:
    """Complete schema for a dataset"""
    name: str
    version: str
    columns: List[ColumnSchema]
    primary_key: Optional[List[str]] = None
    row_count_min: Optional[int] = None
    row_count_max: Optional[int] = None


@dataclass
class ValidationResult:
    """Result of a single validation check"""
    check_name: str
    column: Optional[str]
    passed: bool
    expected: Any
    actual: Any
    severity: str = "error"  # error, warning, info
    message: str = ""
    failed_rows: List[int] = field(default_factory=list)


@dataclass
class ColumnProfile:
    """Statistical profile of a column"""
    name: str
    data_type: str
    total_count: int
    null_count: int
    null_percentage: float
    unique_count: int
    unique_percentage: float
    # Numeric stats
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    mean: Optional[float] = None
    median: Optional[float] = None
    std_dev: Optional[float] = None
    percentile_25: Optional[float] = None
    percentile_75: Optional[float] = None
    # String stats
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    avg_length: Optional[float] = None
    # Pattern detection
    detected_pattern: Optional[str] = None
    top_values: List[Tuple[str, int]] = field(default_factory=list)


@dataclass
class DataProfile:
    """Complete profile of a dataset"""
    name: str
    row_count: int
    column_count: int
    columns: List[ColumnProfile]
    duplicate_rows: int
    memory_size_bytes: int
    profile_timestamp: str


@dataclass
class QualityScore:
    """Overall quality score for a dataset"""
    completeness: float  # % of non-null values
    uniqueness: float    # % of unique values where expected
    validity: float      # % passing validation rules
    consistency: float   # % passing cross-column checks
    accuracy: float      # % matching expected patterns
    overall: float       # weighted average
