# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from threat_modeler_base import *  # noqa: F403,E402


class STRIDECategory(Enum):
    SPOOFING = "Spoofing"
    TAMPERING = "Tampering"
    REPUDIATION = "Repudiation"
    INFORMATION_DISCLOSURE = "Information Disclosure"
    DENIAL_OF_SERVICE = "Denial of Service"
    ELEVATION_OF_PRIVILEGE = "Elevation of Privilege"
@dataclass
class Threat:
    category: str
    name: str
    description: str
    attack_vector: str
    impact: str
    likelihood: int  # 1-5
    severity: int    # 1-5
    mitigations: List[str]

    @property
    def risk_score(self) -> int:
        return self.likelihood * self.severity

    @property
    def risk_level(self) -> str:
        score = self.risk_score
        if score >= 20:
            return "Critical"
        elif score >= 12:
            return "High"
        elif score >= 6:
            return "Medium"
        else:
            return "Low"
