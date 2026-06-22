# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from root_cause_analyzer_base import *  # noqa: F403,E402


class AnalysisMethod(Enum):
    FIVE_WHY = "5-Why"
    FISHBONE = "Fishbone"
    FAULT_TREE = "Fault Tree"
    KEPNER_TREGOE = "Kepner-Tregoe"


class RootCauseCategory(Enum):
    MAN = "Man (People)"
    MACHINE = "Machine (Equipment)"
    MATERIAL = "Material"
    METHOD = "Method (Process)"
    MEASUREMENT = "Measurement"
    ENVIRONMENT = "Environment"
    MANAGEMENT = "Management (Policy)"
    SOFTWARE = "Software/Data"


class SeverityLevel(Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


@dataclass
class WhyStep:
    """A single step in 5-Why analysis."""
    level: int
    question: str
    answer: str
    evidence: str = ""
    verified: bool = False


@dataclass
class FishboneCause:
    """A cause in fishbone analysis."""
    category: str
    cause: str
    sub_causes: List[str] = field(default_factory=list)
    is_root: bool = False
    evidence: str = ""


@dataclass
class FaultEvent:
    """An event in fault tree analysis."""
    event_id: str
    description: str
    is_basic: bool = True  # Basic events have no children
    gate_type: str = "OR"  # OR, AND
    children: List[str] = field(default_factory=list)
    probability: Optional[float] = None


@dataclass
class RootCauseFinding:
    """Identified root cause with evidence."""
    cause_id: str
    description: str
    category: str
    evidence: List[str] = field(default_factory=list)
    contributing_factors: List[str] = field(default_factory=list)
    systemic: bool = False  # Whether it's a systemic vs. local issue


@dataclass
class CAPARecommendation:
    """Corrective or preventive action recommendation."""
    action_id: str
    action_type: str  # "Corrective" or "Preventive"
    description: str
    addresses_cause: str  # cause_id
    priority: str
    estimated_effort: str
    responsible_role: str
    effectiveness_criteria: List[str] = field(default_factory=list)


@dataclass
class RootCauseAnalysis:
    """Complete root cause analysis result."""
    investigation_id: str
    problem_statement: str
    analysis_method: str
    root_causes: List[RootCauseFinding]
    recommendations: List[CAPARecommendation]
    analysis_details: Dict
    confidence_level: float
    investigator_notes: List[str] = field(default_factory=list)
