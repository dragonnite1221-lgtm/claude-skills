# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from secret_scanner_base import *  # noqa: F403,E402


class Severity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
@dataclass
class SecretPattern:
    pattern_id: str
    name: str
    description: str
    regex: str
    severity: Severity
    file_extensions: List[str]
    recommendation: str
@dataclass
class SecretFinding:
    pattern_id: str
    name: str
    severity: Severity
    file_path: str
    line_number: int
    matched_text: str
    recommendation: str
