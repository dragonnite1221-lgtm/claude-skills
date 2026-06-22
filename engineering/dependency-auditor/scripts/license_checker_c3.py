# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from license_checker_base import *  # noqa: F403,E402
from license_checker_p0 import DependencyLicense, LicenseInfo, LicenseType  # noqa: F401,E501


class LicenseCheckerMixin3:
    def _scan_package_directory(self, package_path: Path) -> Optional[LicenseInfo]:
        """Scan package directory for license information."""
        license_files = ['LICENSE', 'LICENSE.txt', 'LICENSE.md', 'COPYING', 'README.md', 'package.json']
        
        for license_file in license_files:
            file_path = package_path / license_file
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Try to detect license from content
                    if license_file == 'package.json':
                        # Parse JSON for license field
                        try:
                            data = json.loads(content)
                            license_field = data.get('license')
                            if license_field:
                                return self._resolve_license_info(license_field)
                        except:
                            continue
                    else:
                        # Analyze text content
                        detected_license = self._detect_license_from_text(content)
                        if detected_license:
                            return self.license_database.get(detected_license)
                except Exception:
                    continue
        
        return None
    def _generate_license_summary(self, dependencies: List[DependencyLicense]) -> Dict[str, Any]:
        """Generate summary of license distribution."""
        summary = {
            'total_dependencies': len(dependencies),
            'license_types': {},
            'risk_levels': {},
            'unknown_licenses': 0,
            'direct_dependencies': 0,
            'transitive_dependencies': 0
        }
        
        for dep in dependencies:
            # Count by license type
            license_type = dep.license_detected.license_type.value
            summary['license_types'][license_type] = summary['license_types'].get(license_type, 0) + 1
            
            # Count by risk level
            risk_level = dep.license_detected.risk_level.value
            summary['risk_levels'][risk_level] = summary['risk_levels'].get(risk_level, 0) + 1
            
            # Count unknowns
            if dep.license_detected.license_type == LicenseType.UNKNOWN:
                summary['unknown_licenses'] += 1
            
            # Count direct vs transitive
            if dep.direct:
                summary['direct_dependencies'] += 1
            else:
                summary['transitive_dependencies'] += 1
        
        return summary
