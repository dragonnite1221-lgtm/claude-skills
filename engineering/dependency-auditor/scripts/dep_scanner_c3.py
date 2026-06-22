# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from dep_scanner_base import *  # noqa: F403,E402
from dep_scanner_p0 import Dependency  # noqa: F401,E501


class DependencyScannerMixin3:
    def _parse_package_json(self, file_path: Path) -> List[Dependency]:
        """Parse package.json for Node.js dependencies."""
        dependencies = []
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Parse dependencies
            for dep_type in ['dependencies', 'devDependencies']:
                if dep_type in data:
                    for name, version in data[dep_type].items():
                        dep = Dependency(
                            name=name,
                            version=version.replace('^', '').replace('~', '').replace('>=', '').replace('<=', ''),
                            ecosystem='npm',
                            direct=True
                        )
                        dependencies.append(dep)
        
        except Exception as e:
            print(f"Error parsing package.json: {e}")
        
        return dependencies
    def _parse_package_lock(self, file_path: Path) -> List[Dependency]:
        """Parse package-lock.json for Node.js transitive dependencies."""
        dependencies = []
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            if 'packages' in data:
                for path, pkg_info in data['packages'].items():
                    if path == '':  # Skip root package
                        continue
                    
                    name = path.split('/')[-1] if '/' in path else path
                    version = pkg_info.get('version', '')
                    
                    dep = Dependency(
                        name=name,
                        version=version,
                        ecosystem='npm',
                        direct=False,
                        description=pkg_info.get('description', '')
                    )
                    dependencies.append(dep)
        
        except Exception as e:
            print(f"Error parsing package-lock.json: {e}")
        
        return dependencies
    def _parse_yarn_lock(self, file_path: Path) -> List[Dependency]:
        """Parse yarn.lock for Node.js dependencies."""
        dependencies = []
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Simple yarn.lock parsing
            packages = re.findall(r'^([^#\s][^:]+):\s*\n(?:\s+.*\n)*?\s+version\s+"([^"]+)"', content, re.MULTILINE)
            
            for package_spec, version in packages:
                name = package_spec.split('@')[0] if '@' in package_spec else package_spec
                name = name.strip('"')
                
                dep = Dependency(
                    name=name,
                    version=version,
                    ecosystem='npm',
                    direct=False
                )
                dependencies.append(dep)
        
        except Exception as e:
            print(f"Error parsing yarn.lock: {e}")
        
        return dependencies
    def _parse_requirements_txt(self, file_path: Path) -> List[Dependency]:
        """Parse requirements.txt for Python dependencies."""
        dependencies = []
        
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#') and not line.startswith('-'):
                    # Parse package==version or package>=version patterns
                    match = re.match(r'^([a-zA-Z0-9_-]+)([><=!]+)(.+)$', line)
                    if match:
                        name, operator, version = match.groups()
                        dep = Dependency(
                            name=name,
                            version=version,
                            ecosystem='pypi',
                            direct=True
                        )
                        dependencies.append(dep)
        
        except Exception as e:
            print(f"Error parsing requirements.txt: {e}")
        
        return dependencies
