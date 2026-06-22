# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from compliance_checker_base import *  # noqa: F403,E402
from compliance_checker_p0 import ComplianceControl  # noqa: F401,E501


class ComplianceCheckerMixin6:
    def _check_security_testing(self):
        """PCI-DSS Req 11: Check security testing."""
        evidence = []
        status = 'failed'

        # Check for test configuration
        test_patterns = [
            r'security.*test',
            r'penetration.*test',
            r'vulnerability.*scan'
        ]

        for pattern in test_patterns:
            files = self._search_files(pattern, case_sensitive=False)
            if files:
                evidence.extend(files[:3])
                status = 'passed'
                break

        # Check for SAST/DAST configuration
        sast_configs = ['.snyk', '.semgrep.yml', 'sonar-project.properties']
        for config in sast_configs:
            if (self.target_path / config).exists():
                evidence.append(config)
                if status == 'failed':
                    status = 'warning'
                break

        self.controls.append(ComplianceControl(
            control_id='PCI-DSS-11.3',
            framework='PCI-DSS',
            category='Security Testing',
            title='Vulnerability Assessment',
            description='Verify regular security testing is performed',
            status=status,
            evidence=evidence[:5],
            recommendation='Configure SAST/DAST scanning and schedule quarterly penetration tests',
            severity='high' if status == 'failed' else 'low'
        ))
    def _check_hipaa_access_control(self):
        """HIPAA 164.312(a)(1): Access Control."""
        evidence = []
        status = 'failed'

        # Check for user identification
        auth_patterns = [r'user.*id', r'authentication', r'identity']
        for pattern in auth_patterns:
            files = self._search_files(pattern, case_sensitive=False)
            if files:
                evidence.extend(files[:3])
                status = 'passed'
                break

        self.controls.append(ComplianceControl(
            control_id='HIPAA-164.312(a)(1)',
            framework='HIPAA',
            category='Access Control',
            title='Unique User Identification',
            description='Verify unique user identification for accessing PHI',
            status=status,
            evidence=evidence[:5],
            recommendation='Implement unique user accounts with individual credentials for all PHI access',
            severity='critical' if status == 'failed' else 'low'
        ))
    def _check_hipaa_audit(self):
        """HIPAA 164.312(b): Audit Controls."""
        evidence = []
        status = 'failed'

        audit_patterns = [r'audit.*trail', r'access.*log', r'phi.*log']
        for pattern in audit_patterns:
            files = self._search_files(pattern, case_sensitive=False)
            if files:
                evidence.extend(files[:3])
                status = 'passed'
                break

        self.controls.append(ComplianceControl(
            control_id='HIPAA-164.312(b)',
            framework='HIPAA',
            category='Audit Controls',
            title='PHI Access Audit Trail',
            description='Verify audit trails for PHI access are maintained',
            status=status,
            evidence=evidence[:5],
            recommendation='Implement comprehensive audit logging for all PHI access with who/what/when/where',
            severity='critical' if status == 'failed' else 'low'
        ))
