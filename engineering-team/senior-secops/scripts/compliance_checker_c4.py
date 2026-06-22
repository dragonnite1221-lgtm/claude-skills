# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from compliance_checker_base import *  # noqa: F403,E402
from compliance_checker_p0 import ComplianceControl  # noqa: F401,E501


class ComplianceCheckerMixin4:
    def _check_change_management(self):
        """SOC 2 CC8: Check change management controls."""
        evidence = []
        status = 'failed'

        # Check for CI/CD configuration
        ci_configs = [
            '.github/workflows',
            '.gitlab-ci.yml',
            'Jenkinsfile',
            '.circleci/config.yml',
            'azure-pipelines.yml'
        ]

        for config in ci_configs:
            config_path = self.target_path / config
            if config_path.exists():
                evidence.append(str(config))
                status = 'passed'
                break

        # Check for branch protection indicators
        branch_patterns = [r'protected.*branch', r'require.*review', r'pull.*request']
        for pattern in branch_patterns:
            files = self._search_files(pattern, case_sensitive=False)
            if files:
                evidence.extend(files[:2])
                break

        self.controls.append(ComplianceControl(
            control_id='SOC2-CC8.1',
            framework='SOC 2',
            category='Change Management',
            title='CI/CD and Code Review',
            description='Verify automated deployment pipeline and code review process',
            status=status,
            evidence=evidence[:5],
            recommendation='Implement CI/CD pipeline with required code reviews and branch protection',
            severity='medium' if status == 'failed' else 'low'
        ))
    def _check_data_encryption(self):
        """PCI-DSS Req 3: Check encryption at rest."""
        evidence = []
        status = 'failed'

        encryption_patterns = [
            r'AES',
            r'encrypt',
            r'crypto\.createCipher',
            r'Fernet',
            r'KMS',
            r'encryptedField'
        ]

        for pattern in encryption_patterns:
            files = self._search_files(pattern)
            if files:
                evidence.extend(files[:3])
                status = 'passed'
                break

        self.controls.append(ComplianceControl(
            control_id='PCI-DSS-3.5',
            framework='PCI-DSS',
            category='Protect Stored Data',
            title='Encryption at Rest',
            description='Verify sensitive data is encrypted at rest',
            status=status,
            evidence=evidence[:5],
            recommendation='Implement AES-256 encryption for sensitive data storage using approved libraries',
            severity='critical' if status == 'failed' else 'low'
        ))
    def _check_transmission_encryption(self):
        """PCI-DSS Req 4: Check encryption in transit."""
        evidence = []
        status = 'failed'

        tls_patterns = [
            r'https://',
            r'TLS',
            r'SSL',
            r'secure.*cookie',
            r'HSTS'
        ]

        for pattern in tls_patterns:
            files = self._search_files(pattern, case_sensitive=False)
            if files:
                evidence.extend(files[:3])
                status = 'passed'
                break

        self.controls.append(ComplianceControl(
            control_id='PCI-DSS-4.1',
            framework='PCI-DSS',
            category='Encrypt Transmissions',
            title='TLS/HTTPS Enforcement',
            description='Verify TLS 1.2+ is enforced for all transmissions',
            status=status,
            evidence=evidence[:5],
            recommendation='Enforce HTTPS with TLS 1.2+, enable HSTS, use secure cookies',
            severity='critical' if status == 'failed' else 'low'
        ))
