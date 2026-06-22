# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from rollback_generator_base import *  # noqa: F403,E402


class RollbackTrigger(Enum):
    """Types of rollback triggers"""
    MANUAL = "manual"
    AUTOMATED = "automated"
    THRESHOLD_BASED = "threshold_based"
    TIME_BASED = "time_based"


class RollbackUrgency(Enum):
    """Rollback urgency levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EMERGENCY = "emergency"


@dataclass
class RollbackStep:
    """Individual rollback step"""
    step_id: str
    name: str
    description: str
    script_type: str  # sql, bash, api, manual
    script_content: str
    estimated_duration_minutes: int
    dependencies: List[str]
    validation_commands: List[str]
    success_criteria: List[str]
    failure_escalation: str
    rollback_order: int


@dataclass
class RollbackPhase:
    """Rollback phase containing multiple steps"""
    phase_name: str
    description: str
    urgency_level: str
    estimated_duration_minutes: int
    prerequisites: List[str]
    steps: List[RollbackStep]
    validation_checkpoints: List[str]
    communication_requirements: List[str]
    risk_level: str


@dataclass
class RollbackTriggerCondition:
    """Conditions that trigger automatic rollback"""
    trigger_id: str
    name: str
    condition: str
    metric_threshold: Optional[Dict[str, Any]]
    evaluation_window_minutes: int
    auto_execute: bool
    escalation_contacts: List[str]


@dataclass
class DataRecoveryPlan:
    """Data recovery and restoration plan"""
    recovery_method: str  # backup_restore, point_in_time, event_replay
    backup_location: str
    recovery_scripts: List[str]
    data_validation_queries: List[str]
    estimated_recovery_time_minutes: int
    recovery_dependencies: List[str]


@dataclass
class CommunicationTemplate:
    """Communication template for rollback scenarios"""
    template_type: str  # start, progress, completion, escalation
    audience: str  # technical, business, executive, customers
    subject: str
    body: str
    urgency: str
    delivery_methods: List[str]


@dataclass
class RollbackRunbook:
    """Complete rollback runbook"""
    runbook_id: str
    migration_id: str
    created_at: str
    rollback_phases: List[RollbackPhase]
    trigger_conditions: List[RollbackTriggerCondition]
    data_recovery_plan: DataRecoveryPlan
    communication_templates: List[CommunicationTemplate]
    escalation_matrix: Dict[str, Any]
    validation_checklist: List[str]
    post_rollback_procedures: List[str]
    emergency_contacts: List[Dict[str, str]]
