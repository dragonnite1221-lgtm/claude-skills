# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from security_scanner_base import *  # noqa: F403,E402


class SecurityScannerMixin2:
    def _is_false_positive(self, line: str, file_path: str) -> bool:
        """Check if finding is likely a false positive."""
        # Skip comments
        stripped = line.strip()
        if stripped.startswith('#') or stripped.startswith('//') or stripped.startswith('*'):
            return True

        # Skip test files for some patterns
        if 'test' in file_path.lower() or 'spec' in file_path.lower():
            return True

        # Skip example/sample values
        lower_line = line.lower()
        if any(skip in lower_line for skip in ['example', 'sample', 'placeholder', 'xxx', 'your_']):
            return True

        return False
    def _calculate_severity(self, default: str, file_path: str, category: str) -> str:
        """Calculate severity based on context."""
        # Increase severity for production-related files
        if any(prod in file_path.lower() for prod in ['prod', 'production', 'deploy']):
            if default == 'high':
                return 'critical'
            if default == 'medium':
                return 'high'

        # Decrease severity for config examples
        if 'example' in file_path.lower() or 'sample' in file_path.lower():
            if default == 'critical':
                return 'high'
            if default == 'high':
                return 'medium'

        return default
    def _get_recommendation(self, category: str) -> str:
        """Get remediation recommendation for category."""
        recommendations = {
            'secrets': 'Remove hardcoded secrets. Use environment variables or a secrets manager (HashiCorp Vault, AWS Secrets Manager).',
            'injection': 'Use parameterized queries or prepared statements. Never concatenate user input into queries.',
            'xss': 'Always escape or sanitize user input before rendering. Use framework-provided escaping functions.',
            'path-traversal': 'Validate and sanitize file paths. Use allowlists for permitted directories.',
        }
        return recommendations.get(category, 'Review and remediate the security issue.')
    def _print_summary(self, result: Dict):
        """Print scan summary."""
        print("\n" + "=" * 60)
        print("SECURITY SCAN SUMMARY")
        print("=" * 60)
        print(f"Target: {result['target']}")
        print(f"Files scanned: {result['files_scanned']}")
        print(f"Scan duration: {result['scan_duration_seconds']}s")
        print(f"Total findings: {result['total_findings']}")
        print()

        if result['severity_counts']:
            print("Findings by severity:")
            for severity in ['critical', 'high', 'medium', 'low', 'info']:
                count = result['severity_counts'].get(severity, 0)
                if count > 0:
                    print(f"  {severity.upper()}: {count}")
        print("=" * 60)

        if result['total_findings'] > 0:
            print("\nTop findings:")
            for finding in result['findings'][:5]:
                print(f"\n  [{finding['severity'].upper()}] {finding['title']}")
                print(f"  File: {finding['file_path']}:{finding['line_number']}")
                print(f"  {finding['description']}")
