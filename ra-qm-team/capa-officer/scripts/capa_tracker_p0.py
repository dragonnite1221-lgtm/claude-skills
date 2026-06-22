# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from capa_tracker_base import *  # noqa: F403,E402


class CAPAStatus(Enum):
    OPEN = "Open"
    INVESTIGATION = "Investigation"
    ACTION_PLANNING = "Action Planning"
    IMPLEMENTATION = "Implementation"
    VERIFICATION = "Verification"
    CLOSED_EFFECTIVE = "Closed - Effective"
    CLOSED_INEFFECTIVE = "Closed - Ineffective"


class CAPASeverity(Enum):
    CRITICAL = "Critical"
    MAJOR = "Major"
    MINOR = "Minor"


class CAPASource(Enum):
    COMPLAINT = "Customer Complaint"
    AUDIT = "Internal Audit"
    EXTERNAL_AUDIT = "External Audit"
    NONCONFORMANCE = "Nonconformance"
    MANAGEMENT_REVIEW = "Management Review"
    TREND_ANALYSIS = "Trend Analysis"
    REGULATORY = "Regulatory Feedback"
    OTHER = "Other"


@dataclass
class CAPA:
    capa_number: str
    title: str
    description: str
    source: CAPASource
    severity: CAPASeverity
    status: CAPAStatus
    open_date: str
    target_date: str
    owner: str
    root_cause: str = ""
    corrective_action: str = ""
    verification_date: Optional[str] = None
    close_date: Optional[str] = None
    days_open: int = 0
    is_overdue: bool = False


@dataclass
class CAPAMetrics:
    total_capas: int
    open_capas: int
    closed_capas: int
    overdue_capas: int
    avg_cycle_time: float
    effectiveness_rate: float
    by_status: Dict[str, int]
    by_severity: Dict[str, int]
    by_source: Dict[str, int]
    overdue_list: List[Dict]
    recommendations: List[str]
