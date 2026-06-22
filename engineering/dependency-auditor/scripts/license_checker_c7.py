# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from license_checker_base import *  # noqa: F403,E402
from license_checker_p0 import RiskLevel  # noqa: F401,E501


class LicenseCheckerMixin7:
    def generate_report(self, analysis_results: Dict[str, Any], format: str = 'text') -> str:
        """Generate compliance report in specified format."""
        if format == 'json':
            # Convert dataclass objects for JSON serialization
            serializable_results = analysis_results.copy()
            serializable_results['dependencies'] = [
                {
                    'name': dep.name,
                    'version': dep.version,
                    'ecosystem': dep.ecosystem,
                    'direct': dep.direct,
                    'license_declared': dep.license_declared,
                    'license_detected': asdict(dep.license_detected) if dep.license_detected else None,
                    'confidence': dep.confidence
                }
                for dep in analysis_results['dependencies']
            ]
            serializable_results['conflicts'] = [asdict(conflict) for conflict in analysis_results['conflicts']]
            return json.dumps(serializable_results, indent=2, default=str)
        
        # Text format report
        report = []
        report.append("=" * 60)
        report.append("LICENSE COMPLIANCE REPORT")
        report.append("=" * 60)
        report.append(f"Analysis Date: {analysis_results['timestamp']}")
        report.append(f"Project: {analysis_results['project_path']}")
        report.append(f"Project License: {analysis_results['project_license'] or 'Unknown'}")
        report.append("")
        
        # Summary
        summary = analysis_results['license_summary']
        report.append("SUMMARY:")
        report.append(f"  Total Dependencies: {summary['total_dependencies']}")
        report.append(f"  Compliance Score: {analysis_results['compliance_score']:.1f}/100")
        report.append(f"  Overall Risk: {analysis_results['risk_assessment']['overall_risk']}")
        report.append(f"  License Conflicts: {len(analysis_results['conflicts'])}")
        report.append("")
        
        # License distribution
        report.append("LICENSE DISTRIBUTION:")
        for license_type, count in summary['license_types'].items():
            report.append(f"  {license_type.title()}: {count}")
        report.append("")
        
        # Risk breakdown
        report.append("RISK BREAKDOWN:")
        for risk_level, count in summary['risk_levels'].items():
            report.append(f"  {risk_level.title()}: {count}")
        report.append("")
        
        # Conflicts
        if analysis_results['conflicts']:
            report.append("LICENSE CONFLICTS:")
            report.append("-" * 30)
            for conflict in analysis_results['conflicts']:
                report.append(f"Conflict: {conflict.dependency2} ({conflict.license2})")
                report.append(f"  Issue: {conflict.description}")
                report.append(f"  Severity: {conflict.severity.value.upper()}")
                report.append(f"  Resolutions: {', '.join(conflict.resolution_options[:2])}")
                report.append("")
        
        # High-risk dependencies
        high_risk_deps = [dep for dep in analysis_results['dependencies'] 
                         if dep.license_detected.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]]
        if high_risk_deps:
            report.append("HIGH-RISK DEPENDENCIES:")
            report.append("-" * 30)
            for dep in high_risk_deps[:10]:  # Top 10
                license_name = dep.license_detected.spdx_id or dep.license_detected.name
                report.append(f"  {dep.name} v{dep.version}: {license_name} ({dep.license_detected.risk_level.value.upper()})")
            report.append("")
        
        # Recommendations
        if analysis_results['recommendations']:
            report.append("RECOMMENDATIONS:")
            report.append("-" * 20)
            for i, rec in enumerate(analysis_results['recommendations'], 1):
                report.append(f"{i}. {rec}")
            report.append("")
        
        report.append("=" * 60)
        return '\n'.join(report)
