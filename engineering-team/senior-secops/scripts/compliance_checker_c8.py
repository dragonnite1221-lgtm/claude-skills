# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from compliance_checker_base import *  # noqa: F403,E402
from compliance_checker_p0 import ComplianceControl  # noqa: F401,E501


class ComplianceCheckerMixin8:
    def _check_gdpr_security(self):
        """GDPR Article 32: Security of processing."""
        evidence = []
        status = 'failed'

        security_patterns = [r'encrypt', r'pseudonymization', r'anonymization']
        for pattern in security_patterns:
            files = self._search_files(pattern, case_sensitive=False)
            if files:
                evidence.extend(files[:3])
                status = 'passed'
                break

        self.controls.append(ComplianceControl(
            control_id='GDPR-32',
            framework='GDPR',
            category='Security',
            title='Pseudonymization and Encryption',
            description='Verify appropriate security measures for personal data',
            status=status,
            evidence=evidence[:5],
            recommendation='Implement encryption and pseudonymization for personal data processing',
            severity='high' if status == 'failed' else 'low'
        ))
    def _check_breach_notification(self):
        """GDPR Article 33/34: Breach notification."""
        evidence = []
        status = 'failed'

        breach_patterns = [
            r'breach.*notification',
            r'incident.*response',
            r'security.*incident'
        ]

        for pattern in breach_patterns:
            files = self._search_files(pattern, case_sensitive=False)
            if files:
                evidence.extend(files[:3])
                status = 'passed'
                break

        # Check for incident response documentation
        incident_docs = ['SECURITY.md', 'docs/incident-response.md', '.github/SECURITY.md']
        for doc in incident_docs:
            if (self.target_path / doc).exists():
                evidence.append(doc)
                if status == 'failed':
                    status = 'warning'
                break

        self.controls.append(ComplianceControl(
            control_id='GDPR-33',
            framework='GDPR',
            category='Breach Notification',
            title='Incident Response Procedure',
            description='Verify breach notification procedures are documented',
            status=status,
            evidence=evidence[:5],
            recommendation='Document incident response procedures with 72-hour notification capability',
            severity='high' if status == 'failed' else 'low'
        ))
    def _check_data_deletion(self):
        """GDPR Article 17: Right to erasure."""
        evidence = []
        status = 'failed'

        deletion_patterns = [
            r'delete.*user',
            r'erasure',
            r'right.*forgotten',
            r'data.*deletion',
            r'gdpr.*delete'
        ]

        for pattern in deletion_patterns:
            files = self._search_files(pattern, case_sensitive=False)
            if files:
                evidence.extend(files[:3])
                status = 'passed'
                break

        self.controls.append(ComplianceControl(
            control_id='GDPR-17',
            framework='GDPR',
            category='Data Subject Rights',
            title='Right to Erasure',
            description='Verify data deletion capability is implemented',
            status=status,
            evidence=evidence[:5],
            recommendation='Implement complete user data deletion including all backups and third-party systems',
            severity='high' if status == 'failed' else 'low'
        ))
