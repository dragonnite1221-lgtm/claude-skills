# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from dep_scanner_base import *  # noqa: F403,E402
from dep_scanner_p0 import Dependency  # noqa: F401,E501


class DependencyScannerMixin4:
    def _parse_pyproject_toml(self, file_path: Path) -> List[Dependency]:
        """Parse pyproject.toml for Python dependencies."""
        dependencies = []
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Simple TOML parsing for dependencies
            dep_section = re.search(r'\[tool\.poetry\.dependencies\](.*?)(?=\[|\Z)', content, re.DOTALL)
            if dep_section:
                for line in dep_section.group(1).split('\n'):
                    match = re.match(r'^([a-zA-Z0-9_-]+)\s*=\s*["\']([^"\']+)["\']', line.strip())
                    if match:
                        name, version = match.groups()
                        if name != 'python':
                            dep = Dependency(
                                name=name,
                                version=version.replace('^', '').replace('~', ''),
                                ecosystem='pypi',
                                direct=True
                            )
                            dependencies.append(dep)
        
        except Exception as e:
            print(f"Error parsing pyproject.toml: {e}")
        
        return dependencies
    def _parse_pipfile_lock(self, file_path: Path) -> List[Dependency]:
        """Parse Pipfile.lock for Python dependencies."""
        dependencies = []
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            for section in ['default', 'develop']:
                if section in data:
                    for name, info in data[section].items():
                        version = info.get('version', '').replace('==', '')
                        dep = Dependency(
                            name=name,
                            version=version,
                            ecosystem='pypi',
                            direct=(section == 'default')
                        )
                        dependencies.append(dep)
        
        except Exception as e:
            print(f"Error parsing Pipfile.lock: {e}")
        
        return dependencies
    def _parse_poetry_lock(self, file_path: Path) -> List[Dependency]:
        """Parse poetry.lock for Python dependencies."""
        dependencies = []
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Extract package entries from TOML
            packages = re.findall(r'\[\[package\]\]\nname\s*=\s*"([^"]+)"\nversion\s*=\s*"([^"]+)"', content)
            
            for name, version in packages:
                dep = Dependency(
                    name=name,
                    version=version,
                    ecosystem='pypi',
                    direct=False
                )
                dependencies.append(dep)
        
        except Exception as e:
            print(f"Error parsing poetry.lock: {e}")
        
        return dependencies
    def _parse_go_mod(self, file_path: Path) -> List[Dependency]:
        """Parse go.mod for Go dependencies."""
        dependencies = []
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Parse require block
            require_match = re.search(r'require\s*\((.*?)\)', content, re.DOTALL)
            if require_match:
                requires = require_match.group(1)
                for line in requires.split('\n'):
                    match = re.match(r'\s*([^\s]+)\s+v?([^\s]+)', line.strip())
                    if match:
                        name, version = match.groups()
                        dep = Dependency(
                            name=name,
                            version=version,
                            ecosystem='go',
                            direct=True
                        )
                        dependencies.append(dep)
        
        except Exception as e:
            print(f"Error parsing go.mod: {e}")
        
        return dependencies
    def _parse_go_sum(self, file_path: Path) -> List[Dependency]:
        """Parse go.sum for Go dependency checksums."""
        return []  # go.sum mainly contains checksums, dependencies are in go.mod
