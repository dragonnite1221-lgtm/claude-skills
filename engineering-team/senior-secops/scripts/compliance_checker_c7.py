# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from compliance_checker_base import *  # noqa: F403,E402
from compliance_checker_p0 import ComplianceControl  # noqa: F401,E501


class ComplianceCheckerMixin7:
    def _check_hipaa_integrity(self):
        """HIPAA 164.312(c)(1): Integrity Controls."""
        evidence = []
        status = 'failed'

        integrity_patterns = [r'checksum', r'hash', r'signature', r'integrity']
        for pattern in integrity_patterns:
            files = self._search_files(pattern, case_sensitive=False)
            if files:
                evidence.extend(files[:3])
                status = 'passed'
                break

        self.controls.append(ComplianceControl(
            control_id='HIPAA-164.312(c)(1)',
            framework='HIPAA',
            category='Integrity',
            title='Data Integrity Controls',
            description='Verify mechanisms to protect PHI from improper alteration',
            status=status,
            evidence=evidence[:5],
            recommendation='Implement checksums, digital signatures, or hashing for PHI integrity verification',
            severity='high' if status == 'failed' else 'low'
        ))
    def _check_hipaa_authentication(self):
        """HIPAA 164.312(d): Authentication."""
        evidence = []
        status = 'failed'

        auth_patterns = [r'mfa', r'two.*factor', r'biometric', r'token.*auth']
        for pattern in auth_patterns:
            files = self._search_files(pattern, case_sensitive=False)
            if files:
                evidence.extend(files[:3])
                status = 'passed'
                break

        self.controls.append(ComplianceControl(
            control_id='HIPAA-164.312(d)',
            framework='HIPAA',
            category='Authentication',
            title='Person Authentication',
            description='Verify mechanisms to authenticate person or entity accessing PHI',
            status=status,
            evidence=evidence[:5],
            recommendation='Implement multi-factor authentication for all PHI access',
            severity='critical' if status == 'failed' else 'low'
        ))
    def _check_hipaa_transmission(self):
        """HIPAA 164.312(e)(1): Transmission Security."""
        evidence = []
        status = 'failed'

        transmission_patterns = [r'tls', r'ssl', r'https', r'encrypt.*transit']
        for pattern in transmission_patterns:
            files = self._search_files(pattern, case_sensitive=False)
            if files:
                evidence.extend(files[:3])
                status = 'passed'
                break

        self.controls.append(ComplianceControl(
            control_id='HIPAA-164.312(e)(1)',
            framework='HIPAA',
            category='Transmission Security',
            title='PHI Transmission Encryption',
            description='Verify PHI is encrypted during transmission',
            status=status,
            evidence=evidence[:5],
            recommendation='Enforce TLS 1.2+ for all PHI transmissions, implement end-to-end encryption',
            severity='critical' if status == 'failed' else 'low'
        ))
    def _check_privacy_by_design(self):
        """GDPR Article 25: Privacy by design."""
        evidence = []
        status = 'failed'

        privacy_patterns = [
            r'data.*minimization',
            r'privacy.*config',
            r'consent',
            r'gdpr'
        ]

        for pattern in privacy_patterns:
            files = self._search_files(pattern, case_sensitive=False)
            if files:
                evidence.extend(files[:3])
                status = 'passed'
                break

        self.controls.append(ComplianceControl(
            control_id='GDPR-25',
            framework='GDPR',
            category='Privacy by Design',
            title='Data Minimization',
            description='Verify data collection is limited to necessary purposes',
            status=status,
            evidence=evidence[:5],
            recommendation='Implement data minimization, purpose limitation, and privacy-by-default configurations',
            severity='high' if status == 'failed' else 'low'
        ))
