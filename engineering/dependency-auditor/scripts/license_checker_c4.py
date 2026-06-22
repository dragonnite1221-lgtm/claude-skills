# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from license_checker_base import *  # noqa: F403,E402
from license_checker_p0 import DependencyLicense, LicenseConflict, LicenseInfo, LicenseType, RiskLevel  # noqa: F401,E501


class LicenseCheckerMixin4:
    def _detect_license_conflicts(self, project_license: Optional[str], 
                                 dependencies: List[DependencyLicense]) -> List[LicenseConflict]:
        """Detect license compatibility conflicts."""
        conflicts = []
        
        if not project_license:
            # If no project license detected, flag as potential issue
            for dep in dependencies:
                if dep.license_detected.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                    conflicts.append(LicenseConflict(
                        dependency1='Project',
                        license1='Unknown',
                        dependency2=dep.name,
                        license2=dep.license_detected.spdx_id or dep.license_detected.name,
                        conflict_type='Unknown project license',
                        severity=RiskLevel.HIGH,
                        description=f'Project license unknown, dependency {dep.name} has {dep.license_detected.risk_level.value} risk license',
                        resolution_options=['Define project license', 'Review dependency usage']
                    ))
            return conflicts
        
        project_license_info = self.license_database.get(project_license)
        if not project_license_info:
            return conflicts
        
        # Check compatibility with project license
        for dep in dependencies:
            dep_license_id = dep.license_detected.spdx_id or 'UNKNOWN'
            
            # Check compatibility matrix
            if project_license in self.compatibility_matrix:
                compatibility = self.compatibility_matrix[project_license].get(dep_license_id, False)
                
                if not compatibility:
                    severity = self._determine_conflict_severity(project_license_info, dep.license_detected)
                    
                    conflicts.append(LicenseConflict(
                        dependency1='Project',
                        license1=project_license,
                        dependency2=dep.name,
                        license2=dep_license_id,
                        conflict_type='License incompatibility',
                        severity=severity,
                        description=f'Project license {project_license} is incompatible with dependency license {dep_license_id}',
                        resolution_options=self._generate_conflict_resolutions(project_license, dep_license_id)
                    ))
        
        # Check for GPL contamination in permissive projects
        if project_license_info.license_type == LicenseType.PERMISSIVE:
            for dep in dependencies:
                if dep.license_detected.license_type == LicenseType.COPYLEFT_STRONG:
                    conflicts.append(LicenseConflict(
                        dependency1='Project',
                        license1=project_license,
                        dependency2=dep.name,
                        license2=dep.license_detected.spdx_id or dep.license_detected.name,
                        conflict_type='GPL contamination',
                        severity=RiskLevel.CRITICAL,
                        description=f'GPL dependency {dep.name} may contaminate permissive project',
                        resolution_options=['Remove GPL dependency', 'Change project license to GPL', 
                                          'Use dynamic linking', 'Find alternative dependency']
                    ))
        
        return conflicts
    def _determine_conflict_severity(self, project_license: LicenseInfo, dep_license: LicenseInfo) -> RiskLevel:
        """Determine severity of a license conflict."""
        if dep_license.license_type == LicenseType.UNKNOWN:
            return RiskLevel.CRITICAL
        elif (project_license.license_type == LicenseType.PERMISSIVE and 
              dep_license.license_type == LicenseType.COPYLEFT_STRONG):
            return RiskLevel.CRITICAL
        elif dep_license.license_type == LicenseType.PROPRIETARY:
            return RiskLevel.HIGH
        else:
            return RiskLevel.MEDIUM
    def _generate_conflict_resolutions(self, project_license: str, dep_license: str) -> List[str]:
        """Generate resolution options for license conflicts."""
        resolutions = []
        
        if 'GPL' in dep_license:
            resolutions.extend([
                'Find alternative non-GPL dependency',
                'Use dynamic linking if possible',
                'Consider changing project license to GPL-compatible',
                'Remove the dependency if not essential'
            ])
        elif dep_license == 'PROPRIETARY':
            resolutions.extend([
                'Obtain commercial license',
                'Find open-source alternative',
                'Remove dependency if not essential',
                'Negotiate license terms'
            ])
        else:
            resolutions.extend([
                'Review license compatibility carefully',
                'Consult legal counsel',
                'Find alternative dependency',
                'Consider license exception'
            ])
        
        return resolutions
