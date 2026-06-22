# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from license_checker_base import *  # noqa: F403,E402


class LicenseCheckerMixin1:
    def analyze_project(self, project_path: str, dependency_inventory: Optional[str] = None) -> Dict[str, Any]:
        """Analyze license compliance for a project."""
        project_path = Path(project_path)
        
        analysis_results = {
            'timestamp': datetime.now().isoformat(),
            'project_path': str(project_path),
            'project_license': self._detect_project_license(project_path),
            'dependencies': [],
            'license_summary': {},
            'conflicts': [],
            'compliance_score': 0.0,
            'risk_assessment': {},
            'recommendations': []
        }
        
        # Load dependencies from inventory or scan project
        if dependency_inventory:
            dependencies = self._load_dependency_inventory(dependency_inventory)
        else:
            dependencies = self._scan_project_dependencies(project_path)
        
        # Analyze each dependency's license
        for dep in dependencies:
            license_info = self._analyze_dependency_license(dep, project_path)
            analysis_results['dependencies'].append(license_info)
        
        # Generate license summary
        analysis_results['license_summary'] = self._generate_license_summary(
            analysis_results['dependencies']
        )
        
        # Detect conflicts
        analysis_results['conflicts'] = self._detect_license_conflicts(
            analysis_results['project_license'],
            analysis_results['dependencies']
        )
        
        # Calculate compliance score
        analysis_results['compliance_score'] = self._calculate_compliance_score(
            analysis_results['dependencies'],
            analysis_results['conflicts']
        )
        
        # Generate risk assessment
        analysis_results['risk_assessment'] = self._generate_risk_assessment(
            analysis_results['dependencies'],
            analysis_results['conflicts']
        )
        
        # Generate recommendations
        analysis_results['recommendations'] = self._generate_compliance_recommendations(
            analysis_results
        )
        
        return analysis_results
    def _detect_project_license(self, project_path: Path) -> Optional[str]:
        """Detect the main project license."""
        license_files = ['LICENSE', 'LICENSE.txt', 'LICENSE.md', 'COPYING', 'COPYING.txt']
        
        for license_file in license_files:
            license_path = project_path / license_file
            if license_path.exists():
                try:
                    with open(license_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Analyze license content
                    detected_license = self._detect_license_from_text(content)
                    if detected_license:
                        return detected_license
                except Exception as e:
                    print(f"Error reading license file {license_path}: {e}")
        
        return None
    def _detect_license_from_text(self, text: str) -> Optional[str]:
        """Detect license type from text content."""
        text_upper = text.upper()
        
        for license_id, patterns in self.license_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return license_id
        
        # Common license text patterns
        if 'MIT' in text_upper and 'PERMISSION IS HEREBY GRANTED' in text_upper:
            return 'MIT'
        elif 'APACHE LICENSE' in text_upper and 'VERSION 2.0' in text_upper:
            return 'Apache-2.0'
        elif 'GPL' in text_upper and 'VERSION 2' in text_upper:
            return 'GPL-2.0'
        elif 'GPL' in text_upper and 'VERSION 3' in text_upper:
            return 'GPL-3.0'
        
        return None
    def _load_dependency_inventory(self, inventory_path: str) -> List[Dict[str, Any]]:
        """Load dependencies from JSON inventory file."""
        try:
            with open(inventory_path, 'r') as f:
                data = json.load(f)
            
            if 'dependencies' in data:
                return data['dependencies']
            else:
                return data if isinstance(data, list) else []
        except Exception as e:
            print(f"Error loading dependency inventory: {e}")
            return []
