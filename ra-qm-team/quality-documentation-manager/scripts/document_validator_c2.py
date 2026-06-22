# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from document_validator_base import *  # noqa: F403,E402
from document_validator_p0 import DocumentStatus, Severity, ValidationFinding  # noqa: F401,E501


class DocumentValidatorMixin2:
    def _validate_approvals(self):
        """Validate document approval information."""
        if self.document.status in [DocumentStatus.APPROVED.value, DocumentStatus.EFFECTIVE.value]:
            if not self.document.author:
                self.findings.append(ValidationFinding(
                    rule="DOC-APR-001",
                    severity=Severity.MAJOR,
                    message="Document author not identified",
                    recommendation="Document author on signature page"
                ))

            if not self.document.approver:
                self.findings.append(ValidationFinding(
                    rule="DOC-APR-002",
                    severity=Severity.CRITICAL,
                    message="Document approver not identified",
                    recommendation="Obtain required approval signatures"
                ))
    def _validate_change_history(self):
        """Validate change history completeness."""
        history = self.document.change_history

        if not history:
            self.findings.append(ValidationFinding(
                rule="DOC-CHG-001",
                severity=Severity.MAJOR,
                message="Document change history is missing",
                recommendation="Include change history table with revision descriptions"
            ))
            return

        for i, entry in enumerate(history):
            if not entry.get('revision'):
                self.findings.append(ValidationFinding(
                    rule="DOC-CHG-002",
                    severity=Severity.MINOR,
                    message=f"Change history entry {i+1} missing revision number",
                    recommendation="Include revision number for each history entry"
                ))

            if not entry.get('description'):
                self.findings.append(ValidationFinding(
                    rule="DOC-CHG-003",
                    severity=Severity.MINOR,
                    message=f"Change history entry {i+1} missing description",
                    recommendation="Include description of changes for each revision"
                ))

            if not entry.get('date'):
                self.findings.append(ValidationFinding(
                    rule="DOC-CHG-004",
                    severity=Severity.MINOR,
                    message=f"Change history entry {i+1} missing date",
                    recommendation="Include date for each history entry"
                ))
    def _validate_electronic_controls(self):
        """Validate 21 CFR Part 11 requirements for electronic documents."""
        # Audit trail check
        if not self.document.has_audit_trail:
            self.findings.append(ValidationFinding(
                rule="P11-AUD-001",
                severity=Severity.MAJOR,
                message="Electronic document lacks audit trail",
                recommendation="Enable audit trail for 21 CFR Part 11 compliance"
            ))

        # Electronic signature check
        if self.document.has_electronic_signature:
            if self.document.signature_components < 2:
                self.findings.append(ValidationFinding(
                    rule="P11-SIG-001",
                    severity=Severity.CRITICAL,
                    message="Electronic signature uses fewer than 2 identification components",
                    recommendation="Use at least 2 components (e.g., user ID + password)"
                ))
        else:
            if self.document.status in [DocumentStatus.APPROVED.value, DocumentStatus.EFFECTIVE.value]:
                self.findings.append(ValidationFinding(
                    rule="P11-SIG-002",
                    severity=Severity.INFO,
                    message="Document uses handwritten signatures",
                    recommendation="Consider electronic signatures for efficiency"
                ))
    def _calculate_compliance_score(self) -> float:
        """Calculate compliance score based on findings."""
        if not self.findings:
            return 100.0

        # Weight by severity
        deductions = {
            Severity.CRITICAL: 25,
            Severity.MAJOR: 10,
            Severity.MINOR: 3,
            Severity.INFO: 0
        }

        total_deduction = sum(deductions[f.severity] for f in self.findings)
        score = max(0, 100 - total_deduction)

        return score
