# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from document_validator_base import *  # noqa: F403,E402
from document_validator_p0 import Severity  # noqa: F401,E501


class DocumentValidatorMixin3:
    def _generate_recommendations(self) -> List[str]:
        """Generate prioritized recommendations."""
        recommendations = []

        # Critical findings
        critical = [f for f in self.findings if f.severity == Severity.CRITICAL]
        if critical:
            recommendations.append(
                f"URGENT: {len(critical)} critical finding(s) require immediate attention"
            )

        # Major findings
        major = [f for f in self.findings if f.severity == Severity.MAJOR]
        if major:
            recommendations.append(
                f"ACTION: {len(major)} major finding(s) should be addressed within 30 days"
            )

        # Review overdue
        review_overdue = [f for f in self.findings if f.rule == "DOC-DTE-003"]
        if review_overdue:
            recommendations.append(
                "REVIEW: Document is overdue for periodic review. Initiate review process."
            )

        # Part 11 gaps
        p11_findings = [f for f in self.findings if f.rule.startswith("P11")]
        if p11_findings:
            recommendations.append(
                f"COMPLIANCE: {len(p11_findings)} 21 CFR Part 11 gap(s) identified"
            )

        if not recommendations:
            recommendations.append("Document passes validation checks")

        return recommendations
