# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from license_checker_base import *  # noqa: F403,E402
from license_checker_p0 import DependencyLicense, LicenseConflict, LicenseType, RiskLevel  # noqa: F401,E501


class LicenseCheckerMixin5:
    def _calculate_compliance_score(self, dependencies: List[DependencyLicense], 
                                   conflicts: List[LicenseConflict]) -> float:
        """Calculate overall compliance score (0-100)."""
        if not dependencies:
            return 100.0
        
        base_score = 100.0
        
        # Deduct points for unknown licenses
        unknown_count = sum(1 for dep in dependencies 
                           if dep.license_detected.license_type == LicenseType.UNKNOWN)
        base_score -= (unknown_count / len(dependencies)) * 30
        
        # Deduct points for high-risk licenses
        high_risk_count = sum(1 for dep in dependencies 
                             if dep.license_detected.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL])
        base_score -= (high_risk_count / len(dependencies)) * 20
        
        # Deduct points for conflicts
        if conflicts:
            critical_conflicts = sum(1 for c in conflicts if c.severity == RiskLevel.CRITICAL)
            high_conflicts = sum(1 for c in conflicts if c.severity == RiskLevel.HIGH)
            
            base_score -= critical_conflicts * 15
            base_score -= high_conflicts * 10
        
        return max(0.0, base_score)
    def _generate_risk_assessment(self, dependencies: List[DependencyLicense], 
                                 conflicts: List[LicenseConflict]) -> Dict[str, Any]:
        """Generate comprehensive risk assessment."""
        return {
            'overall_risk': self._calculate_overall_risk(dependencies, conflicts),
            'license_risk_breakdown': self._calculate_license_risks(dependencies),
            'conflict_summary': {
                'total_conflicts': len(conflicts),
                'critical_conflicts': len([c for c in conflicts if c.severity == RiskLevel.CRITICAL]),
                'high_conflicts': len([c for c in conflicts if c.severity == RiskLevel.HIGH])
            },
            'distribution_risks': self._assess_distribution_risks(dependencies),
            'commercial_risks': self._assess_commercial_risks(dependencies)
        }
    def _calculate_overall_risk(self, dependencies: List[DependencyLicense], 
                               conflicts: List[LicenseConflict]) -> str:
        """Calculate overall project risk level."""
        if any(c.severity == RiskLevel.CRITICAL for c in conflicts):
            return 'CRITICAL'
        elif any(dep.license_detected.risk_level == RiskLevel.CRITICAL for dep in dependencies):
            return 'CRITICAL'
        elif any(c.severity == RiskLevel.HIGH for c in conflicts):
            return 'HIGH'
        elif any(dep.license_detected.risk_level == RiskLevel.HIGH for dep in dependencies):
            return 'HIGH'
        elif any(dep.license_detected.risk_level == RiskLevel.MEDIUM for dep in dependencies):
            return 'MEDIUM'
        else:
            return 'LOW'
    def _calculate_license_risks(self, dependencies: List[DependencyLicense]) -> Dict[str, int]:
        """Calculate breakdown of license risks."""
        risks = {'low': 0, 'medium': 0, 'high': 0, 'critical': 0}
        
        for dep in dependencies:
            risk_level = dep.license_detected.risk_level.value
            risks[risk_level] += 1
        
        return risks
    def _assess_distribution_risks(self, dependencies: List[DependencyLicense]) -> List[str]:
        """Assess risks related to software distribution."""
        risks = []
        
        gpl_deps = [dep for dep in dependencies 
                   if dep.license_detected.license_type == LicenseType.COPYLEFT_STRONG]
        if gpl_deps:
            risks.append(f"GPL dependencies require source code disclosure: {[d.name for d in gpl_deps]}")
        
        proprietary_deps = [dep for dep in dependencies 
                           if dep.license_detected.license_type == LicenseType.PROPRIETARY]
        if proprietary_deps:
            risks.append(f"Proprietary dependencies may require commercial licenses: {[d.name for d in proprietary_deps]}")
        
        unknown_deps = [dep for dep in dependencies 
                       if dep.license_detected.license_type == LicenseType.UNKNOWN]
        if unknown_deps:
            risks.append(f"Unknown licenses pose legal uncertainty: {[d.name for d in unknown_deps]}")
        
        return risks
    def _assess_commercial_risks(self, dependencies: List[DependencyLicense]) -> List[str]:
        """Assess risks for commercial usage."""
        risks = []
        
        agpl_deps = [dep for dep in dependencies 
                    if dep.license_detected.spdx_id == 'AGPL-3.0']
        if agpl_deps:
            risks.append(f"AGPL dependencies trigger copyleft for network services: {[d.name for d in agpl_deps]}")
        
        return risks
