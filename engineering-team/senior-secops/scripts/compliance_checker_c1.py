# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from compliance_checker_base import *  # noqa: F403,E402
from compliance_checker_p0 import ComplianceControl  # noqa: F401,E501


class ComplianceCheckerMixin1:
    def check_pci_dss(self):
        """Check PCI-DSS v4.0 requirements."""
        if self.verbose:
            print("  Checking PCI-DSS v4.0 requirements...")

        # Requirement 3: Protect stored cardholder data
        self._check_data_encryption()

        # Requirement 4: Encrypt transmission of cardholder data
        self._check_transmission_encryption()

        # Requirement 6: Develop and maintain secure systems
        self._check_secure_development()

        # Requirement 8: Identify users and authenticate access
        self._check_strong_authentication()

        # Requirement 10: Log and monitor all access
        self._check_audit_logging()

        # Requirement 11: Test security of systems regularly
        self._check_security_testing()
    def check_hipaa(self):
        """Check HIPAA security rule requirements."""
        if self.verbose:
            print("  Checking HIPAA Security Rule requirements...")

        # 164.312(a)(1): Access Control
        self._check_hipaa_access_control()

        # 164.312(b): Audit Controls
        self._check_hipaa_audit()

        # 164.312(c)(1): Integrity Controls
        self._check_hipaa_integrity()

        # 164.312(d): Person or Entity Authentication
        self._check_hipaa_authentication()

        # 164.312(e)(1): Transmission Security
        self._check_hipaa_transmission()
    def check_gdpr(self):
        """Check GDPR data protection requirements."""
        if self.verbose:
            print("  Checking GDPR requirements...")

        # Article 25: Data protection by design
        self._check_privacy_by_design()

        # Article 32: Security of processing
        self._check_gdpr_security()

        # Article 33/34: Breach notification
        self._check_breach_notification()

        # Article 17: Right to erasure
        self._check_data_deletion()

        # Article 20: Data portability
        self._check_data_export()
    def _check_access_controls_soc2(self):
        """SOC 2 CC1/CC6: Check access control implementation."""
        evidence = []
        status = 'failed'

        # Look for authentication middleware
        auth_patterns = [
            r'authMiddleware',
            r'requireAuth',
            r'isAuthenticated',
            r'@login_required',
            r'@authenticated',
            r'passport\.authenticate',
            r'jwt\.verify',
            r'verifyToken'
        ]

        for pattern in auth_patterns:
            files = self._search_files(pattern)
            if files:
                evidence.extend(files[:3])
                status = 'passed'
                break

        # Check for RBAC implementation
        rbac_patterns = [r'role', r'permission', r'authorize', r'can\(', r'hasRole']
        for pattern in rbac_patterns:
            files = self._search_files(pattern)
            if files:
                evidence.extend(files[:2])
                if status == 'failed':
                    status = 'warning'
                break

        self.controls.append(ComplianceControl(
            control_id='SOC2-CC6.1',
            framework='SOC 2',
            category='Logical Access Controls',
            title='Access Control Implementation',
            description='Verify authentication and authorization controls are implemented',
            status=status,
            evidence=evidence[:5],
            recommendation='Implement authentication middleware and role-based access control (RBAC)',
            severity='high' if status == 'failed' else 'low'
        ))
