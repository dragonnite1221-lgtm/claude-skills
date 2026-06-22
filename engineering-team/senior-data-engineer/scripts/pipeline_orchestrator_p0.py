# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from pipeline_orchestrator_base import *  # noqa: F403,E402


try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def python_string_literal(value: Any) -> str:
    """Return a generated-code-safe Python string literal."""
    return repr(str(value))


def validate_sql_identifier(value: str, label: str = "identifier") -> str:
    """Validate simple SQL identifiers used by template generators."""
    parts = value.split(".")
    if not parts or not all(SQL_IDENTIFIER_RE.match(part) for part in parts):
        raise ValueError(f"Invalid SQL {label}: {value}")
    return value


def validate_python_identifier(value: str, label: str = "identifier") -> str:
    """Validate Python identifiers emitted into generated code."""
    if not PYTHON_IDENTIFIER_RE.match(value):
        raise ValueError(f"Invalid Python {label}: {value}")
    return value


def sql_string_literal(value: str) -> str:
    """Return an escaped SQL string literal for already-validated scalar values."""
    return "'" + value.replace("'", "''") + "'"


def validate_sql_statement(value: Any) -> str:
    """Validate read-only SQL statements accepted by generic task configs."""
    sql = str(value).strip()
    lowered = sql.lower()
    if "\x00" in sql or ";" in sql or "--" in sql or "/*" in sql or "*/" in sql:
        raise ValueError("SQL statements must be a single statement without comments")
    if not (lowered.startswith("select ") or lowered.startswith("with ")):
        raise ValueError("SQL statements must start with SELECT or WITH")
    return sql


def validate_freshness_cutoff(value: str) -> str:
    """Validate freshness cutoff values before embedding them as SQL literals."""
    if AIRFLOW_MACRO_RE.match(value) or ISO_DATE_RE.match(value):
        return value
    raise ValueError(f"Invalid freshness cutoff: {value}")


def validate_dbt_selector(value: str) -> str:
    """Validate dbt selector fragments used by template generators."""
    if not DBT_SELECTOR_RE.match(value):
        raise ValueError(f"Invalid dbt selector: {value}")
    return value


@dataclass
class SourceConfig:
    """Source system configuration."""
    type: str  # postgres, mysql, s3, kafka, api
    connection_id: str
    schema: Optional[str] = None
    tables: List[str] = field(default_factory=list)
    query: Optional[str] = None
    incremental_column: Optional[str] = None
    incremental_strategy: str = "timestamp"  # timestamp, id, cdc


@dataclass
class DestinationConfig:
    """Destination system configuration."""
    type: str  # snowflake, bigquery, redshift, s3, delta
    connection_id: str
    schema: str = "raw"
    write_mode: str = "append"  # append, overwrite, merge
    partition_by: Optional[str] = None
    cluster_by: List[str] = field(default_factory=list)


@dataclass
class TaskConfig:
    """Individual task configuration."""
    task_id: str
    operator: str
    dependencies: List[str] = field(default_factory=list)
    params: Dict[str, Any] = field(default_factory=dict)
    retries: int = 2
    retry_delay_minutes: int = 5
    timeout_minutes: int = 60
    pool: Optional[str] = None
    priority_weight: int = 1


@dataclass
class PipelineConfig:
    """Complete pipeline configuration."""
    name: str
    description: str
    schedule: str  # cron expression or @daily, @hourly
    owner: str = "data-team"
    tags: List[str] = field(default_factory=list)
    catchup: bool = False
    max_active_runs: int = 1
    default_retries: int = 2
    source: Optional[SourceConfig] = None
    destination: Optional[DestinationConfig] = None
    tasks: List[TaskConfig] = field(default_factory=list)


class PipelineGenerator(ABC):
    """Abstract base class for pipeline generators."""

    @abstractmethod
    def generate(self, config: PipelineConfig) -> str:
        """Generate pipeline code from config."""
        pass

    @abstractmethod
    def validate(self, code: str) -> Dict[str, Any]:
        """Validate generated pipeline code."""
        pass
