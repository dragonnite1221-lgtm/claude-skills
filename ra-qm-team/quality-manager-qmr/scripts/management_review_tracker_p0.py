# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from management_review_tracker_base import *  # noqa: F403,E402


class ActionStatus(Enum):
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    ON_HOLD = "On Hold"
    OVERDUE = "Overdue"
    COMPLETE = "Complete"
    VERIFIED = "Verified"


class ActionPriority(Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class InputStatus(Enum):
    NOT_COLLECTED = "Not Collected"
    IN_PROGRESS = "In Progress"
    COMPLETE = "Complete"
    REVIEWED = "Reviewed"


@dataclass
class ReviewInput:
    topic: str
    responsible: str
    status: InputStatus
    data_period: str
    summary: str = ""
    concerns: List[str] = field(default_factory=list)


@dataclass
class ActionItem:
    action_id: str
    description: str
    owner: str
    due_date: str
    priority: ActionPriority
    status: ActionStatus
    source_review: str
    category: str = "Improvement"
    completion_date: Optional[str] = None
    notes: str = ""


@dataclass
class ReviewMetrics:
    complaint_rate: float = 0.0
    complaint_count: int = 0
    capa_open: int = 0
    capa_overdue: int = 0
    capa_effectiveness: float = 0.0
    audit_findings_open: int = 0
    audit_findings_major: int = 0
    first_pass_yield: float = 0.0
    customer_satisfaction: float = 0.0
    training_compliance: float = 0.0


@dataclass
class ManagementReview:
    review_date: str
    review_type: str
    period_start: str
    period_end: str
    inputs: List[ReviewInput]
    actions: List[ActionItem]
    metrics: ReviewMetrics
    decisions: List[str] = field(default_factory=list)
    attendees: List[str] = field(default_factory=list)
