# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from skill_security_auditor_base import *  # noqa: F403,E402


class Severity(IntEnum):
    INFO = 0
    HIGH = 1
    CRITICAL = 2
SEVERITY_LABELS = {
    Severity.INFO: "⚪ INFO",
    Severity.HIGH: "🟡 HIGH",
    Severity.CRITICAL: "🔴 CRITICAL",
}
SEVERITY_NAMES = {
    Severity.INFO: "INFO",
    Severity.HIGH: "HIGH",
    Severity.CRITICAL: "CRITICAL",
}
@dataclass
class Finding:
    severity: Severity
    category: str
    file: str
    line: int
    pattern: str
    risk: str
    fix: str

    def to_dict(self):
        d = asdict(self)
        d["severity"] = SEVERITY_NAMES[self.severity]
        return d
@dataclass
class AuditReport:
    skill_name: str
    skill_path: str
    findings: list = field(default_factory=list)
    files_scanned: int = 0
    scripts_scanned: int = 0
    md_files_scanned: int = 0

    @property
    def critical_count(self):
        return sum(1 for f in self.findings if f.severity == Severity.CRITICAL)

    @property
    def high_count(self):
        return sum(1 for f in self.findings if f.severity == Severity.HIGH)

    @property
    def info_count(self):
        return sum(1 for f in self.findings if f.severity == Severity.INFO)

    @property
    def verdict(self):
        if self.critical_count > 0:
            return "FAIL"
        if self.high_count > 0:
            return "WARN"
        return "PASS"

    def to_dict(self):
        return {
            "skill_name": self.skill_name,
            "skill_path": self.skill_path,
            "verdict": self.verdict,
            "summary": {
                "critical": self.critical_count,
                "high": self.high_count,
                "info": self.info_count,
                "total": len(self.findings),
            },
            "stats": {
                "files_scanned": self.files_scanned,
                "scripts_scanned": self.scripts_scanned,
                "md_files_scanned": self.md_files_scanned,
            },
            "findings": [f.to_dict() for f in self.findings],
        }
