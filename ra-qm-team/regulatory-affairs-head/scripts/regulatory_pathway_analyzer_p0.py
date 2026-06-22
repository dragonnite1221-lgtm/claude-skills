# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from regulatory_pathway_analyzer_base import *  # noqa: F403,E402


class RiskClass(Enum):
    CLASS_I = "I"
    CLASS_IIA = "IIa"
    CLASS_IIB = "IIb"
    CLASS_III = "III"
    CLASS_IV = "IV"


class MarketRegion(Enum):
    US_FDA = "US-FDA"
    EU_MDR = "EU-MDR"
    UK_UKCA = "UK-UKCA"
    HEALTH_CANADA = "Health-Canada"
    AUSTRALIA_TGA = "Australia-TGA"
    JAPAN_PMDA = "Japan-PMDA"


@dataclass
class DeviceProfile:
    """Medical device profile for pathway analysis."""
    device_name: str
    intended_use: str
    device_class: str  # I, IIa, IIb, III
    novel_technology: bool = False
    predicate_available: bool = True
    implantable: bool = False
    life_sustaining: bool = False
    software_component: bool = False
    ai_ml_component: bool = False
    sterile: bool = False
    measuring_function: bool = False
    target_markets: List[str] = field(default_factory=lambda: ["US-FDA", "EU-MDR"])


@dataclass
class PathwayOption:
    """A regulatory pathway option."""
    pathway_name: str
    market: str
    estimated_timeline_months: Tuple[int, int]
    estimated_cost_usd: Tuple[int, int]
    key_requirements: List[str]
    advantages: List[str]
    risks: List[str]
    recommendation_level: str  # "Recommended", "Alternative", "Not Recommended"


@dataclass
class PathwayAnalysis:
    """Complete pathway analysis result."""
    device: DeviceProfile
    recommended_pathways: List[PathwayOption]
    optimal_sequence: List[str]  # Recommended submission order
    total_timeline_months: Tuple[int, int]
    total_estimated_cost: Tuple[int, int]
    critical_success_factors: List[str]
    warnings: List[str]
