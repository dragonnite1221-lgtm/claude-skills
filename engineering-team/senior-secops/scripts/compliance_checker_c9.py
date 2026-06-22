# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from compliance_checker_base import *  # noqa: F403,E402
from compliance_checker_p0 import ComplianceControl  # noqa: F401,E501


class ComplianceCheckerMixin9:
    def _check_data_export(self):
        """GDPR Article 20: Data portability."""
        evidence = []
        status = 'failed'

        export_patterns = [
            r'export.*data',
            r'data.*portability',
            r'download.*data',
            r'gdpr.*export'
        ]

        for pattern in export_patterns:
            files = self._search_files(pattern, case_sensitive=False)
            if files:
                evidence.extend(files[:3])
                status = 'passed'
                break

        self.controls.append(ComplianceControl(
            control_id='GDPR-20',
            framework='GDPR',
            category='Data Subject Rights',
            title='Data Portability',
            description='Verify data export capability is implemented',
            status=status,
            evidence=evidence[:5],
            recommendation='Implement data export in machine-readable format (JSON, CSV)',
            severity='medium' if status == 'failed' else 'low'
        ))
    def _search_files(self, pattern: str, case_sensitive: bool = True) -> List[str]:
        """Search files for pattern matches."""
        matches = []
        flags = 0 if case_sensitive else re.IGNORECASE

        try:
            for root, dirs, files in os.walk(self.target_path):
                # Skip common non-relevant directories
                dirs[:] = [d for d in dirs if d not in {
                    'node_modules', '.git', '__pycache__', 'venv', '.venv',
                    'dist', 'build', 'coverage', '.next'
                }]

                for filename in files:
                    if filename.endswith(('.js', '.ts', '.py', '.go', '.java', '.md', '.yml', '.yaml', '.json')):
                        file_path = Path(root) / filename
                        try:
                            content = file_path.read_text(encoding='utf-8', errors='ignore')
                            if re.search(pattern, content, flags):
                                rel_path = str(file_path.relative_to(self.target_path))
                                matches.append(rel_path)
                                self.files_scanned += 1
                        except Exception:
                            pass
        except Exception:
            pass

        return matches[:10]  # Limit results
    def _calculate_compliance_score(self) -> float:
        """Calculate overall compliance score (0-100)."""
        if not self.controls:
            return 0.0

        # Weight by severity
        severity_weights = {'critical': 4.0, 'high': 3.0, 'medium': 2.0, 'low': 1.0}
        status_scores = {'passed': 1.0, 'warning': 0.5, 'failed': 0.0, 'not_applicable': None}

        total_weight = 0.0
        total_score = 0.0

        for control in self.controls:
            score = status_scores.get(control.status)
            if score is not None:  # Skip N/A
                weight = severity_weights.get(control.severity, 1.0)
                total_weight += weight
                total_score += score * weight

        return round((total_score / total_weight) * 100, 1) if total_weight > 0 else 0.0
    def _get_compliance_level(self, score: float) -> str:
        """Get compliance level from score."""
        if score >= 90:
            return "COMPLIANT"
        elif score >= 70:
            return "PARTIALLY_COMPLIANT"
        elif score >= 50:
            return "NON_COMPLIANT"
        return "CRITICAL_GAPS"
