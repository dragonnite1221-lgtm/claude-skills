# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from compliance_checker_base import *  # noqa: F403,E402
from compliance_checker_p0 import ComplianceControl  # noqa: F401,E501


class ComplianceCheckerMixin2:
    def _check_documentation(self):
        """SOC 2 CC2: Check security documentation."""
        evidence = []
        status = 'failed'

        doc_files = [
            'SECURITY.md',
            'docs/security.md',
            'CONTRIBUTING.md',
            'docs/security-policy.md',
            '.github/SECURITY.md'
        ]

        for doc in doc_files:
            doc_path = self.target_path / doc
            if doc_path.exists():
                evidence.append(str(doc))
                status = 'passed' if 'security' in doc.lower() else 'warning'
                break

        self.controls.append(ComplianceControl(
            control_id='SOC2-CC2.1',
            framework='SOC 2',
            category='Communication and Information',
            title='Security Documentation',
            description='Verify security policies and procedures are documented',
            status=status,
            evidence=evidence,
            recommendation='Create SECURITY.md documenting security policies, incident response, and vulnerability reporting',
            severity='medium' if status == 'failed' else 'low'
        ))
    def _check_risk_assessment(self):
        """SOC 2 CC3: Check risk assessment artifacts."""
        evidence = []
        status = 'failed'

        # Look for security scanning configuration
        scan_configs = [
            '.snyk',
            '.github/workflows/security.yml',
            '.github/workflows/codeql.yml',
            'trivy.yaml',
            '.semgrep.yml',
            'sonar-project.properties'
        ]

        for config in scan_configs:
            config_path = self.target_path / config
            if config_path.exists():
                evidence.append(str(config))
                status = 'passed'
                break

        # Check for dependabot/renovate
        dep_configs = [
            '.github/dependabot.yml',
            'renovate.json',
            '.github/renovate.json'
        ]

        for config in dep_configs:
            config_path = self.target_path / config
            if config_path.exists():
                evidence.append(str(config))
                if status == 'failed':
                    status = 'warning'
                break

        self.controls.append(ComplianceControl(
            control_id='SOC2-CC3.1',
            framework='SOC 2',
            category='Risk Assessment',
            title='Automated Security Scanning',
            description='Verify automated vulnerability scanning is configured',
            status=status,
            evidence=evidence,
            recommendation='Configure automated security scanning (Snyk, CodeQL, Trivy) and dependency updates (Dependabot)',
            severity='high' if status == 'failed' else 'low'
        ))
