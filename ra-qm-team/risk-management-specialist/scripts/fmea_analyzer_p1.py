# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from fmea_analyzer_base import *  # noqa: F403,E402


class FMEAType(Enum):
    DESIGN = "Design FMEA"
    PROCESS = "Process FMEA"
class Severity(Enum):
    INCONSEQUENTIAL = 1
    MINOR = 2
    MODERATE = 3
    SIGNIFICANT = 4
    SERIOUS = 5
    CRITICAL = 6
    SERIOUS_HAZARD = 7
    HAZARDOUS = 8
    HAZARDOUS_NO_WARNING = 9
    CATASTROPHIC = 10
class Occurrence(Enum):
    REMOTE = 1
    LOW = 2
    LOW_MODERATE = 3
    MODERATE = 4
    MODERATE_HIGH = 5
    HIGH = 6
    VERY_HIGH = 7
    EXTREMELY_HIGH = 8
    ALMOST_CERTAIN = 9
    INEVITABLE = 10
class Detection(Enum):
    ALMOST_CERTAIN = 1
    VERY_HIGH = 2
    HIGH = 3
    MODERATE_HIGH = 4
    MODERATE = 5
    LOW_MODERATE = 6
    LOW = 7
    VERY_LOW = 8
    REMOTE = 9
    ABSOLUTELY_UNCERTAIN = 10
@dataclass
class FMEAEntry:
    """Single FMEA line item."""
    item_process: str
    function: str
    failure_mode: str
    effect: str
    severity: int
    cause: str
    occurrence: int
    current_controls: str
    detection: int
    rpn: int = 0
    criticality: str = ""
    recommended_actions: List[str] = field(default_factory=list)
    responsibility: str = ""
    target_date: str = ""
    actions_taken: str = ""
    revised_severity: int = 0
    revised_occurrence: int = 0
    revised_detection: int = 0
    revised_rpn: int = 0

    def calculate_rpn(self):
        self.rpn = self.severity * self.occurrence * self.detection
        if self.severity >= 8:
            self.criticality = "CRITICAL"
        elif self.rpn >= 200:
            self.criticality = "HIGH"
        elif self.rpn >= 100:
            self.criticality = "MEDIUM"
        else:
            self.criticality = "LOW"

    def calculate_revised_rpn(self):
        if self.revised_severity and self.revised_occurrence and self.revised_detection:
            self.revised_rpn = self.revised_severity * self.revised_occurrence * self.revised_detection
@dataclass
class FMEAReport:
    """Complete FMEA analysis report."""
    fmea_type: str
    product_process: str
    team: List[str]
    date: str
    entries: List[FMEAEntry]
    summary: Dict
    risk_reduction_actions: List[Dict]
