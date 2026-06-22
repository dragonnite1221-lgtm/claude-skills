# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from compliance_checker_base import *  # noqa: F403,E402
from compliance_checker_p0 import ComplianceControl  # noqa: F401,E501


class ComplianceCheckerMixin5:
    def _check_secure_development(self):
        """PCI-DSS Req 6: Check secure development practices."""
        evidence = []
        status = 'failed'

        # Check for input validation
        validation_patterns = [
            r'validator',
            r'sanitize',
            r'escape',
            r'zod',
            r'yup',
            r'joi'
        ]

        for pattern in validation_patterns:
            files = self._search_files(pattern, case_sensitive=False)
            if files:
                evidence.extend(files[:3])
                status = 'passed'
                break

        self.controls.append(ComplianceControl(
            control_id='PCI-DSS-6.5',
            framework='PCI-DSS',
            category='Secure Development',
            title='Input Validation',
            description='Verify input validation and sanitization is implemented',
            status=status,
            evidence=evidence[:5],
            recommendation='Use validation libraries (Joi, Zod, validator.js) for all user input',
            severity='high' if status == 'failed' else 'low'
        ))
    def _check_strong_authentication(self):
        """PCI-DSS Req 8: Check authentication requirements."""
        evidence = []
        status = 'failed'

        # Check for session management
        session_patterns = [
            r'session.*timeout',
            r'maxAge',
            r'expiresIn',
            r'session.*expire'
        ]

        for pattern in session_patterns:
            files = self._search_files(pattern, case_sensitive=False)
            if files:
                evidence.extend(files[:3])
                status = 'passed'
                break

        self.controls.append(ComplianceControl(
            control_id='PCI-DSS-8.6',
            framework='PCI-DSS',
            category='Authentication',
            title='Session Management',
            description='Verify session timeout and management controls',
            status=status,
            evidence=evidence[:5],
            recommendation='Implement 15-minute session timeout, secure session tokens, and session invalidation on logout',
            severity='high' if status == 'failed' else 'low'
        ))
    def _check_audit_logging(self):
        """PCI-DSS Req 10: Check audit logging."""
        # Reuse SOC 2 logging check logic
        evidence = []
        status = 'failed'

        log_patterns = [r'audit', r'log.*event', r'security.*log']
        for pattern in log_patterns:
            files = self._search_files(pattern, case_sensitive=False)
            if files:
                evidence.extend(files[:3])
                status = 'passed'
                break

        self.controls.append(ComplianceControl(
            control_id='PCI-DSS-10.2',
            framework='PCI-DSS',
            category='Logging and Monitoring',
            title='Security Event Logging',
            description='Verify security events are logged with sufficient detail',
            status=status,
            evidence=evidence[:5],
            recommendation='Log all authentication events, access to cardholder data, and administrative actions',
            severity='high' if status == 'failed' else 'low'
        ))
