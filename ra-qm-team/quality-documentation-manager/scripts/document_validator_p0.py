# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from document_validator_base import *  # noqa: F403,E402


class DocumentType(Enum):
    QM = "Quality Manual"
    SOP = "Standard Operating Procedure"
    WI = "Work Instruction"
    TF = "Template/Form"
    POL = "Policy"
    SPEC = "Specification"
    PLN = "Plan"
    RPT = "Report"


class DocumentStatus(Enum):
    DRAFT = "Draft"
    REVIEW = "Under Review"
    APPROVED = "Approved"
    EFFECTIVE = "Effective"
    SUPERSEDED = "Superseded"
    OBSOLETE = "Obsolete"


class Severity(Enum):
    CRITICAL = "Critical"
    MAJOR = "Major"
    MINOR = "Minor"
    INFO = "Info"


@dataclass
class ValidationFinding:
    rule: str
    severity: Severity
    message: str
    recommendation: str


@dataclass
class Document:
    number: str
    title: str
    doc_type: str
    revision: str
    status: str
    effective_date: Optional[str] = None
    review_date: Optional[str] = None
    author: Optional[str] = None
    approver: Optional[str] = None
    approval_date: Optional[str] = None
    change_history: List[Dict] = field(default_factory=list)
    has_audit_trail: bool = False
    has_electronic_signature: bool = False
    signature_components: int = 0


@dataclass
class ValidationResult:
    document_number: str
    validation_date: str
    total_findings: int
    critical_findings: int
    major_findings: int
    minor_findings: int
    compliance_score: float
    findings: List[Dict]
    recommendations: List[str]


def format_text_output(result: ValidationResult) -> str:
    """Format validation result as text report."""
    lines = [
        "=" * 70,
        "DOCUMENT VALIDATION REPORT",
        "=" * 70,
        f"Document: {result.document_number}",
        f"Validation Date: {result.validation_date}",
        f"Compliance Score: {result.compliance_score}%",
        "",
        "FINDINGS SUMMARY",
        "-" * 40,
        f"  Critical: {result.critical_findings}",
        f"  Major:    {result.major_findings}",
        f"  Minor:    {result.minor_findings}",
        f"  Total:    {result.total_findings}",
    ]

    if result.findings:
        lines.extend([
            "",
            "DETAILED FINDINGS",
            "-" * 40,
        ])

        for finding in result.findings:
            severity = finding['severity']
            lines.append(f"\n[{severity}] {finding['rule']}")
            lines.append(f"  Issue: {finding['message']}")
            lines.append(f"  Action: {finding['recommendation']}")

    lines.extend([
        "",
        "RECOMMENDATIONS",
        "-" * 40,
    ])

    for i, rec in enumerate(result.recommendations, 1):
        lines.append(f"{i}. {rec}")

    lines.append("=" * 70)
    return "\n".join(lines)
