# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from audit_schedule_optimizer_base import *  # noqa: F403,E402


class RiskLevel(Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
class AuditFrequency(Enum):
    QUARTERLY = 90
    SEMI_ANNUAL = 180
    ANNUAL = 365
    EXTENDED = 540  # 18 months
@dataclass
class Process:
    name: str
    iso_clause: str
    risk_level: RiskLevel
    last_audit_date: Optional[str] = None
    previous_findings: int = 0
    criticality_score: int = 5  # 1-10 scale
    notes: str = ""
@dataclass
class AuditSlot:
    process_name: str
    iso_clause: str
    scheduled_date: str
    risk_level: str
    priority_score: float
    days_overdue: int = 0
    rationale: str = ""
@dataclass
class AuditSchedule:
    generated_date: str
    schedule_period: str
    total_audits: int
    audits_by_quarter: Dict[str, int]
    schedule: List[Dict]
    recommendations: List[str]
