# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from license_checker_base import *  # noqa: F403,E402
from license_checker_p0 import DependencyLicense, LicenseInfo  # noqa: F401,E501


class LicenseCheckerMixin2:
    def _scan_project_dependencies(self, project_path: Path) -> List[Dict[str, Any]]:
        """Basic dependency scanning - in practice, would integrate with dep_scanner.py."""
        dependencies = []
        
        # Simple package.json parsing as example
        package_json = project_path / 'package.json'
        if package_json.exists():
            try:
                with open(package_json, 'r') as f:
                    data = json.load(f)
                
                for dep_type in ['dependencies', 'devDependencies']:
                    if dep_type in data:
                        for name, version in data[dep_type].items():
                            dependencies.append({
                                'name': name,
                                'version': version,
                                'ecosystem': 'npm',
                                'direct': True
                            })
            except Exception as e:
                print(f"Error parsing package.json: {e}")
        
        return dependencies
    def _analyze_dependency_license(self, dependency: Dict[str, Any], project_path: Path) -> DependencyLicense:
        """Analyze license information for a single dependency."""
        dep_license = DependencyLicense(
            name=dependency['name'],
            version=dependency.get('version', ''),
            ecosystem=dependency.get('ecosystem', ''),
            direct=dependency.get('direct', False),
            license_declared=dependency.get('license'),
            license_detected=None,
            license_files=[],
            confidence=0.0
        )
        
        # Try to detect license from various sources
        declared_license = dependency.get('license')
        if declared_license:
            license_info = self._resolve_license_info(declared_license)
            if license_info:
                dep_license.license_detected = license_info
                dep_license.confidence = 0.9
        
        # For unknown licenses, try to find license files in node_modules (example)
        if not dep_license.license_detected and dep_license.ecosystem == 'npm':
            node_modules_path = project_path / 'node_modules' / dep_license.name
            if node_modules_path.exists():
                license_info = self._scan_package_directory(node_modules_path)
                if license_info:
                    dep_license.license_detected = license_info
                    dep_license.confidence = 0.7
        
        # Default to unknown if no license detected
        if not dep_license.license_detected:
            dep_license.license_detected = self.license_database['UNKNOWN']
            dep_license.confidence = 0.0
        
        return dep_license
    def _resolve_license_info(self, license_string: str) -> Optional[LicenseInfo]:
        """Resolve license string to LicenseInfo object."""
        if not license_string:
            return None
        
        license_string = license_string.strip()
        
        # Direct SPDX ID match
        if license_string in self.license_database:
            return self.license_database[license_string]
        
        # Common variations and mappings
        license_mappings = {
            'mit': 'MIT',
            'apache': 'Apache-2.0',
            'apache-2.0': 'Apache-2.0',
            'apache 2.0': 'Apache-2.0',
            'bsd': 'BSD-3-Clause',
            'bsd-3-clause': 'BSD-3-Clause',
            'bsd-2-clause': 'BSD-2-Clause',
            'gpl-2.0': 'GPL-2.0',
            'gpl-3.0': 'GPL-3.0',
            'lgpl-2.1': 'LGPL-2.1',
            'lgpl-3.0': 'LGPL-3.0',
            'mpl-2.0': 'MPL-2.0',
            'isc': 'ISC',
            'unlicense': 'MIT',  # Treat as permissive
            'public domain': 'MIT',  # Treat as permissive
            'proprietary': 'PROPRIETARY',
            'commercial': 'PROPRIETARY'
        }
        
        license_lower = license_string.lower()
        for pattern, mapped_license in license_mappings.items():
            if pattern in license_lower:
                return self.license_database.get(mapped_license)
        
        return None
