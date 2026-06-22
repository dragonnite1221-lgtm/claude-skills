# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from license_checker_base import *  # noqa: F403,E402
from license_checker_p0 import LicenseType, RiskLevel  # noqa: F401,E501


class LicenseCheckerMixin6:
    def _generate_compliance_recommendations(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Generate actionable compliance recommendations."""
        recommendations = []
        
        # Address critical issues first
        critical_conflicts = [c for c in analysis_results['conflicts'] 
                             if c.severity == RiskLevel.CRITICAL]
        if critical_conflicts:
            recommendations.append("CRITICAL: Address license conflicts immediately before any distribution")
            for conflict in critical_conflicts[:3]:  # Top 3
                recommendations.append(f"  • {conflict.description}")
        
        # Unknown licenses
        unknown_count = analysis_results['license_summary']['unknown_licenses']
        if unknown_count > 0:
            recommendations.append(f"Investigate and clarify licenses for {unknown_count} dependencies with unknown licensing")
        
        # GPL contamination
        gpl_deps = [dep for dep in analysis_results['dependencies'] 
                   if dep.license_detected.license_type == LicenseType.COPYLEFT_STRONG]
        if gpl_deps and analysis_results.get('project_license') in ['MIT', 'Apache-2.0', 'BSD-3-Clause']:
            recommendations.append("Consider removing GPL dependencies or changing project license for permissive project")
        
        # Compliance score
        if analysis_results['compliance_score'] < 70:
            recommendations.append("Overall compliance score is low - prioritize license cleanup")
        
        return recommendations
