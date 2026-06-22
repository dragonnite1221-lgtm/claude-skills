# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from migration_planner_base import *  # noqa: F403,E402


class MigrationType(Enum):
    """Migration type enumeration"""
    DATABASE = "database"
    SERVICE = "service"
    INFRASTRUCTURE = "infrastructure"
    DATA = "data"
    API = "api"


class MigrationComplexity(Enum):
    """Migration complexity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskLevel(Enum):
    """Risk assessment levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class MigrationConstraint:
    """Migration constraint definition"""
    type: str
    description: str
    impact: str
    mitigation: str


@dataclass
class MigrationPhase:
    """Individual migration phase"""
    name: str
    description: str
    duration_hours: int
    dependencies: List[str]
    validation_criteria: List[str]
    rollback_triggers: List[str]
    tasks: List[str]
    risk_level: str
    resources_required: List[str]


@dataclass
class RiskItem:
    """Individual risk assessment item"""
    category: str
    description: str
    probability: str  # low, medium, high
    impact: str  # low, medium, high
    severity: str  # low, medium, high, critical
    mitigation: str
    owner: str


@dataclass
class MigrationPlan:
    """Complete migration plan structure"""
    migration_id: str
    source_system: str
    target_system: str
    migration_type: str
    complexity: str
    estimated_duration_hours: int
    phases: List[MigrationPhase]
    risks: List[RiskItem]
    success_criteria: List[str]
    rollback_plan: Dict[str, Any]
    stakeholders: List[str]
    created_at: str
