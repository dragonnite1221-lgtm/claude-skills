# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from document_validator_base import *  # noqa: F403,E402
from document_validator_p0 import DocumentStatus, Severity, ValidationFinding  # noqa: F401,E501


class DocumentValidatorMixin1:
    def _validate_status_lifecycle(self):
        """Validate document status and lifecycle."""
        status = self.document.status

        if not status:
            self.findings.append(ValidationFinding(
                rule="DOC-STS-001",
                severity=Severity.MAJOR,
                message="Document status is missing",
                recommendation="Assign appropriate document status"
            ))
            return

        valid_statuses = [s.value for s in DocumentStatus]
        if status not in valid_statuses:
            self.findings.append(ValidationFinding(
                rule="DOC-STS-002",
                severity=Severity.MAJOR,
                message=f"Invalid document status: {status}",
                recommendation=f"Use one of: {', '.join(valid_statuses)}"
            ))

        # Check status-specific requirements
        if status == DocumentStatus.EFFECTIVE.value:
            if not self.document.effective_date:
                self.findings.append(ValidationFinding(
                    rule="DOC-STS-003",
                    severity=Severity.MAJOR,
                    message="Effective document missing effective date",
                    recommendation="Add effective date for effective documents"
                ))

        if status == DocumentStatus.APPROVED.value:
            if not self.document.approval_date:
                self.findings.append(ValidationFinding(
                    rule="DOC-STS-004",
                    severity=Severity.MAJOR,
                    message="Approved document missing approval date",
                    recommendation="Add approval date for approved documents"
                ))
    def _validate_dates(self):
        """Validate document dates."""
        # Check effective date
        if self.document.effective_date:
            try:
                eff_date = datetime.strptime(self.document.effective_date, "%Y-%m-%d")
                if eff_date > self.today:
                    self.findings.append(ValidationFinding(
                        rule="DOC-DTE-001",
                        severity=Severity.INFO,
                        message="Effective date is in the future",
                        recommendation="Verify planned effective date is correct"
                    ))
            except ValueError:
                self.findings.append(ValidationFinding(
                    rule="DOC-DTE-002",
                    severity=Severity.MINOR,
                    message="Invalid effective date format",
                    recommendation="Use YYYY-MM-DD format for dates"
                ))

        # Check review date
        if self.document.review_date:
            try:
                review_date = datetime.strptime(self.document.review_date, "%Y-%m-%d")
                if review_date < self.today:
                    self.findings.append(ValidationFinding(
                        rule="DOC-DTE-003",
                        severity=Severity.MAJOR,
                        message="Document is overdue for review",
                        recommendation="Initiate periodic review process"
                    ))
                elif review_date < self.today + timedelta(days=30):
                    self.findings.append(ValidationFinding(
                        rule="DOC-DTE-004",
                        severity=Severity.MINOR,
                        message="Document review due within 30 days",
                        recommendation="Plan for upcoming review"
                    ))
            except ValueError:
                self.findings.append(ValidationFinding(
                    rule="DOC-DTE-005",
                    severity=Severity.MINOR,
                    message="Invalid review date format",
                    recommendation="Use YYYY-MM-DD format for dates"
                ))
        else:
            if self.document.status == DocumentStatus.EFFECTIVE.value:
                self.findings.append(ValidationFinding(
                    rule="DOC-DTE-006",
                    severity=Severity.MINOR,
                    message="Effective document missing review date",
                    recommendation="Add next review date (typically 1-3 years from effective)"
                ))
