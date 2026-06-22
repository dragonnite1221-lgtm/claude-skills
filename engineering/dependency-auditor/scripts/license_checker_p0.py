# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from license_checker_base import *  # noqa: F403,E402


class LicenseType(Enum):
    """License classification types."""
    PERMISSIVE = "permissive"
    COPYLEFT_STRONG = "copyleft_strong"
    COPYLEFT_WEAK = "copyleft_weak"
    PROPRIETARY = "proprietary"
    DUAL = "dual"
    UNKNOWN = "unknown"


class RiskLevel(Enum):
    """Risk assessment levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class LicenseInfo:
    """Represents license information for a dependency."""
    name: str
    spdx_id: Optional[str]
    license_type: LicenseType
    risk_level: RiskLevel
    description: str
    restrictions: List[str]
    obligations: List[str]
    compatibility: Dict[str, bool]


@dataclass
class DependencyLicense:
    """Represents a dependency with its license information."""
    name: str
    version: str
    ecosystem: str
    direct: bool
    license_declared: Optional[str]
    license_detected: Optional[LicenseInfo]
    license_files: List[str]
    confidence: float


@dataclass
class LicenseConflict:
    """Represents a license compatibility conflict."""
    dependency1: str
    license1: str
    dependency2: str
    license2: str
    conflict_type: str
    severity: RiskLevel
    description: str
    resolution_options: List[str]
