# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from compliance_checker_base import *  # noqa: F403,E402
from compliance_checker_p0 import ComplianceControl  # noqa: F401,E501


class ComplianceCheckerMixin3:
    def _check_authentication(self):
        """SOC 2 CC6: Check authentication strength."""
        evidence = []
        status = 'failed'

        # Check for MFA/2FA
        mfa_patterns = [r'mfa', r'2fa', r'totp', r'authenticator', r'twoFactor']
        for pattern in mfa_patterns:
            files = self._search_files(pattern, case_sensitive=False)
            if files:
                evidence.extend(files[:2])
                status = 'passed'
                break

        # Check for password hashing
        hash_patterns = [r'bcrypt', r'argon2', r'scrypt', r'pbkdf2']
        for pattern in hash_patterns:
            files = self._search_files(pattern, case_sensitive=False)
            if files:
                evidence.extend(files[:2])
                if status == 'failed':
                    status = 'warning'
                break

        self.controls.append(ComplianceControl(
            control_id='SOC2-CC6.2',
            framework='SOC 2',
            category='Authentication',
            title='Strong Authentication',
            description='Verify multi-factor authentication and secure password storage',
            status=status,
            evidence=evidence[:5],
            recommendation='Implement MFA/2FA and use bcrypt/argon2 for password hashing',
            severity='critical' if status == 'failed' else 'low'
        ))
    def _check_logging(self):
        """SOC 2 CC7: Check audit logging implementation."""
        evidence = []
        status = 'failed'

        # Check for logging configuration
        log_patterns = [
            r'winston',
            r'pino',
            r'bunyan',
            r'logging\.getLogger',
            r'log\.info',
            r'logger\.',
            r'audit.*log'
        ]

        for pattern in log_patterns:
            files = self._search_files(pattern)
            if files:
                evidence.extend(files[:3])
                status = 'passed'
                break

        # Check for structured logging
        struct_patterns = [r'json.*log', r'structured.*log', r'log.*format']
        for pattern in struct_patterns:
            files = self._search_files(pattern, case_sensitive=False)
            if files:
                evidence.extend(files[:2])
                break

        self.controls.append(ComplianceControl(
            control_id='SOC2-CC7.1',
            framework='SOC 2',
            category='System Operations',
            title='Audit Logging',
            description='Verify comprehensive audit logging is implemented',
            status=status,
            evidence=evidence[:5],
            recommendation='Implement structured audit logging with security events (auth, access, changes)',
            severity='high' if status == 'failed' else 'low'
        ))
