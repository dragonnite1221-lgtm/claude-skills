# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from release_planner_base import *  # noqa: F403,E402


class RiskLevel(Enum):
    """Risk levels for release components."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ComponentStatus(Enum):
    """Status of release components."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    READY = "ready"
    BLOCKED = "blocked"
    FAILED = "failed"


@dataclass
class Feature:
    """Represents a feature in the release."""
    id: str
    title: str
    description: str
    type: str  # feature, bugfix, security, breaking_change, etc.
    assignee: str
    status: ComponentStatus
    pull_request_url: Optional[str] = None
    issue_url: Optional[str] = None
    risk_level: RiskLevel = RiskLevel.MEDIUM
    test_coverage_required: float = 80.0
    test_coverage_actual: Optional[float] = None
    requires_migration: bool = False
    migration_complexity: str = "simple"  # simple, moderate, complex
    breaking_changes: List[str] = None
    dependencies: List[str] = None
    qa_approved: bool = False
    security_approved: bool = False
    pm_approved: bool = False
    
    def __post_init__(self):
        if self.breaking_changes is None:
            self.breaking_changes = []
        if self.dependencies is None:
            self.dependencies = []


@dataclass
class QualityGate:
    """Quality gate requirements."""
    name: str
    required: bool
    status: ComponentStatus
    details: Optional[str] = None
    threshold: Optional[float] = None
    actual_value: Optional[float] = None


@dataclass
class Stakeholder:
    """Stakeholder for release communication."""
    name: str
    role: str
    contact: str
    notification_type: str  # email, slack, teams
    critical_path: bool = False


@dataclass
class RollbackStep:
    """Individual rollback step."""
    order: int
    description: str
    command: Optional[str] = None
    estimated_time: str = "5 minutes"
    risk_level: RiskLevel = RiskLevel.LOW
    verification: str = ""
