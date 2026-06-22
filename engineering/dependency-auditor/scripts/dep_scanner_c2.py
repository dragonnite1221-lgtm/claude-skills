# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from dep_scanner_base import *  # noqa: F403,E402
from dep_scanner_p0 import Dependency, Vulnerability  # noqa: F401,E501


class DependencyScannerMixin2:
    def scan_project(self, project_path: str) -> Dict[str, Any]:
        """Scan a project directory for dependencies and vulnerabilities."""
        project_path = Path(project_path)
        
        if not project_path.exists():
            raise FileNotFoundError(f"Project path does not exist: {project_path}")
        
        scan_results = {
            'timestamp': datetime.now().isoformat(),
            'project_path': str(project_path),
            'dependencies': [],
            'vulnerabilities_found': 0,
            'high_severity_count': 0,
            'medium_severity_count': 0,
            'low_severity_count': 0,
            'ecosystems': set(),
            'scan_summary': {},
            'recommendations': []
        }
        
        # Find and parse dependency files
        for file_pattern, parser in self.supported_files.items():
            matching_files = list(project_path.rglob(file_pattern))
            
            for dep_file in matching_files:
                try:
                    dependencies = parser(dep_file)
                    scan_results['dependencies'].extend(dependencies)
                    
                    for dep in dependencies:
                        scan_results['ecosystems'].add(dep.ecosystem)
                        
                        # Check for vulnerabilities
                        vulnerabilities = self._check_vulnerabilities(dep)
                        dep.vulnerabilities = vulnerabilities
                        
                        scan_results['vulnerabilities_found'] += len(vulnerabilities)
                        
                        for vuln in vulnerabilities:
                            if vuln.severity == 'HIGH':
                                scan_results['high_severity_count'] += 1
                            elif vuln.severity == 'MEDIUM':
                                scan_results['medium_severity_count'] += 1
                            else:
                                scan_results['low_severity_count'] += 1
                
                except Exception as e:
                    print(f"Error parsing {dep_file}: {e}")
                    continue
        
        scan_results['ecosystems'] = list(scan_results['ecosystems'])
        scan_results['scan_summary'] = self._generate_scan_summary(scan_results)
        scan_results['recommendations'] = self._generate_recommendations(scan_results)
        
        return scan_results
    def _check_vulnerabilities(self, dependency: Dependency) -> List[Vulnerability]:
        """Check if a dependency has known vulnerabilities."""
        vulnerabilities = []
        
        # Check package name (exact match and common variations)
        package_names = [dependency.name, dependency.name.lower()]
        
        for pkg_name in package_names:
            if pkg_name in self.known_vulnerabilities:
                for vuln in self.known_vulnerabilities[pkg_name]:
                    if self._version_matches_vulnerability(dependency.version, vuln.affected_versions):
                        vulnerabilities.append(vuln)
        
        return vulnerabilities
    def _version_matches_vulnerability(self, version: str, affected_pattern: str) -> bool:
        """Check if a version matches a vulnerability pattern."""
        # Simple version matching - in production, use proper semver library
        try:
            # Handle common patterns like "<4.17.21", ">=1.0.0 <1.6.0"
            if '<' in affected_pattern and '>' not in affected_pattern:
                # Pattern like "<4.17.21"
                max_version = affected_pattern.replace('<', '').strip()
                return self._compare_versions(version, max_version) < 0
            elif '>=' in affected_pattern and '<' in affected_pattern:
                # Pattern like ">=1.0.0 <1.6.0"
                parts = affected_pattern.split('<')
                min_part = parts[0].replace('>=', '').strip()
                max_part = parts[1].strip()
                return (self._compare_versions(version, min_part) >= 0 and 
                       self._compare_versions(version, max_part) < 0)
        except:
            pass
        
        return False
    def _compare_versions(self, v1: str, v2: str) -> int:
        """Simple version comparison. Returns -1, 0, or 1."""
        try:
            def normalize(v):
                return [int(x) for x in re.sub(r'(\.0+)*$','', v).split('.')]
            
            v1_parts = normalize(v1)
            v2_parts = normalize(v2)
            
            if v1_parts < v2_parts:
                return -1
            elif v1_parts > v2_parts:
                return 1
            else:
                return 0
        except:
            return 0
