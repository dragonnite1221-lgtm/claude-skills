# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from document_validator_base import *  # noqa: F403,E402
from document_validator_p0 import Document, Severity, ValidationFinding, ValidationResult  # noqa: F401,E501


class DocumentValidatorMixin0:
    """Validator for quality documentation compliance."""
    DOC_NUMBER_PATTERN = r'^([A-Z]{2,4})-(\d{2,3})-(\d{3,4})(?:-([A-Z]|\d{2}))?$'
    VALID_PREFIXES = ['QM', 'SOP', 'WI', 'TF', 'POL', 'SPEC', 'PLN', 'RPT']
    VALID_CATEGORIES = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10']
    def __init__(self, document: Document):
        self.document = document
        self.today = datetime.now()
        self.findings: List[ValidationFinding] = []
    def validate(self) -> ValidationResult:
        """Run all validation checks."""
        self._validate_document_number()
        self._validate_title()
        self._validate_status_lifecycle()
        self._validate_dates()
        self._validate_approvals()
        self._validate_change_history()
        self._validate_electronic_controls()

        # Calculate compliance score
        score = self._calculate_compliance_score()

        # Generate recommendations
        recommendations = self._generate_recommendations()

        # Count findings by severity
        critical = len([f for f in self.findings if f.severity == Severity.CRITICAL])
        major = len([f for f in self.findings if f.severity == Severity.MAJOR])
        minor = len([f for f in self.findings if f.severity == Severity.MINOR])

        return ValidationResult(
            document_number=self.document.number,
            validation_date=self.today.strftime("%Y-%m-%d"),
            total_findings=len(self.findings),
            critical_findings=critical,
            major_findings=major,
            minor_findings=minor,
            compliance_score=round(score, 1),
            findings=[asdict(f) for f in self.findings],
            recommendations=recommendations
        )
    def _validate_document_number(self):
        """Validate document numbering convention."""
        number = self.document.number

        if not number:
            self.findings.append(ValidationFinding(
                rule="DOC-NUM-001",
                severity=Severity.CRITICAL,
                message="Document number is missing",
                recommendation="Assign document number per numbering procedure"
            ))
            return

        match = re.match(self.DOC_NUMBER_PATTERN, number)
        if not match:
            self.findings.append(ValidationFinding(
                rule="DOC-NUM-002",
                severity=Severity.MAJOR,
                message=f"Document number '{number}' does not match standard format",
                recommendation="Use format: PREFIX-CATEGORY-SEQUENCE[-REVISION] (e.g., SOP-02-001-A)"
            ))
            return

        prefix, category, sequence, revision = match.groups()

        if prefix not in self.VALID_PREFIXES:
            self.findings.append(ValidationFinding(
                rule="DOC-NUM-003",
                severity=Severity.MAJOR,
                message=f"Invalid document type prefix: {prefix}",
                recommendation=f"Use one of: {', '.join(self.VALID_PREFIXES)}"
            ))

        if category not in self.VALID_CATEGORIES:
            self.findings.append(ValidationFinding(
                rule="DOC-NUM-004",
                severity=Severity.MINOR,
                message=f"Non-standard category code: {category}",
                recommendation=f"Standard categories are: {', '.join(self.VALID_CATEGORIES)}"
            ))
    def _validate_title(self):
        """Validate document title."""
        title = self.document.title

        if not title:
            self.findings.append(ValidationFinding(
                rule="DOC-TTL-001",
                severity=Severity.MAJOR,
                message="Document title is missing",
                recommendation="Provide descriptive document title"
            ))
            return

        if len(title) < 10:
            self.findings.append(ValidationFinding(
                rule="DOC-TTL-002",
                severity=Severity.MINOR,
                message="Document title is very short",
                recommendation="Use descriptive title that clearly identifies content"
            ))

        if len(title) > 100:
            self.findings.append(ValidationFinding(
                rule="DOC-TTL-003",
                severity=Severity.MINOR,
                message="Document title exceeds recommended length",
                recommendation="Keep title under 100 characters"
            ))
