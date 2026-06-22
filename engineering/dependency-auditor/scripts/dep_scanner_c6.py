# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from dep_scanner_base import *  # noqa: F403,E402


class DependencyScannerMixin6:
    def _generate_scan_summary(self, scan_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of the scan results."""
        total_deps = len(scan_results['dependencies'])
        unique_deps = len(set(dep.name for dep in scan_results['dependencies']))
        
        return {
            'total_dependencies': total_deps,
            'unique_dependencies': unique_deps,
            'ecosystems_found': len(scan_results['ecosystems']),
            'vulnerable_dependencies': len([dep for dep in scan_results['dependencies'] if dep.vulnerabilities]),
            'vulnerability_breakdown': {
                'high': scan_results['high_severity_count'],
                'medium': scan_results['medium_severity_count'],
                'low': scan_results['low_severity_count']
            }
        }
    def _generate_recommendations(self, scan_results: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations based on scan results."""
        recommendations = []
        
        high_count = scan_results['high_severity_count']
        medium_count = scan_results['medium_severity_count']
        
        if high_count > 0:
            recommendations.append(f"URGENT: Address {high_count} high-severity vulnerabilities immediately")
        
        if medium_count > 0:
            recommendations.append(f"Schedule fixes for {medium_count} medium-severity vulnerabilities within 30 days")
        
        vulnerable_deps = [dep for dep in scan_results['dependencies'] if dep.vulnerabilities]
        if vulnerable_deps:
            for dep in vulnerable_deps[:3]:  # Top 3 most critical
                for vuln in dep.vulnerabilities:
                    if vuln.fixed_version:
                        recommendations.append(f"Update {dep.name} from {dep.version} to {vuln.fixed_version} to fix {vuln.id}")
        
        if len(scan_results['ecosystems']) > 3:
            recommendations.append("Consider consolidating package managers to reduce complexity")
        
        return recommendations
    def generate_report(self, scan_results: Dict[str, Any], format: str = 'text') -> str:
        """Generate a human-readable or JSON report."""
        if format == 'json':
            # Convert Dependency objects to dicts for JSON serialization
            serializable_results = scan_results.copy()
            serializable_results['dependencies'] = [
                {
                    'name': dep.name,
                    'version': dep.version,
                    'ecosystem': dep.ecosystem,
                    'direct': dep.direct,
                    'license': dep.license,
                    'vulnerabilities': [asdict(vuln) for vuln in dep.vulnerabilities]
                }
                for dep in scan_results['dependencies']
            ]
            return json.dumps(serializable_results, indent=2, default=str)
        
        # Text format report
        report = []
        report.append("=" * 60)
        report.append("DEPENDENCY SECURITY SCAN REPORT")
        report.append("=" * 60)
        report.append(f"Scan Date: {scan_results['timestamp']}")
        report.append(f"Project: {scan_results['project_path']}")
        report.append("")
        
        # Summary
        summary = scan_results['scan_summary']
        report.append("SUMMARY:")
        report.append(f"  Total Dependencies: {summary['total_dependencies']}")
        report.append(f"  Unique Dependencies: {summary['unique_dependencies']}")
        report.append(f"  Ecosystems: {', '.join(scan_results['ecosystems'])}")
        report.append(f"  Vulnerabilities Found: {scan_results['vulnerabilities_found']}")
        report.append(f"    High Severity: {summary['vulnerability_breakdown']['high']}")
        report.append(f"    Medium Severity: {summary['vulnerability_breakdown']['medium']}")
        report.append(f"    Low Severity: {summary['vulnerability_breakdown']['low']}")
        report.append("")
        
        # Vulnerable dependencies
        vulnerable_deps = [dep for dep in scan_results['dependencies'] if dep.vulnerabilities]
        if vulnerable_deps:
            report.append("VULNERABLE DEPENDENCIES:")
            report.append("-" * 30)
            
            for dep in vulnerable_deps:
                report.append(f"Package: {dep.name} v{dep.version} ({dep.ecosystem})")
                for vuln in dep.vulnerabilities:
                    report.append(f"  • {vuln.id}: {vuln.summary}")
                    report.append(f"    Severity: {vuln.severity} (CVSS: {vuln.cvss_score})")
                    if vuln.fixed_version:
                        report.append(f"    Fixed in: {vuln.fixed_version}")
                    report.append("")
        
        # Recommendations
        if scan_results['recommendations']:
            report.append("RECOMMENDATIONS:")
            report.append("-" * 20)
            for i, rec in enumerate(scan_results['recommendations'], 1):
                report.append(f"{i}. {rec}")
            report.append("")
        
        report.append("=" * 60)
        return '\n'.join(report)
