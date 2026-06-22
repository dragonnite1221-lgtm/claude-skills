# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from dep_scanner_base import *  # noqa: F403,E402
from dep_scanner_p0 import Dependency  # noqa: F401,E501


class DependencyScannerMixin5:
    def _parse_cargo_toml(self, file_path: Path) -> List[Dependency]:
        """Parse Cargo.toml for Rust dependencies."""
        dependencies = []
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Parse [dependencies] section
            dep_section = re.search(r'\[dependencies\](.*?)(?=\[|\Z)', content, re.DOTALL)
            if dep_section:
                for line in dep_section.group(1).split('\n'):
                    match = re.match(r'^([a-zA-Z0-9_-]+)\s*=\s*["\']([^"\']+)["\']', line.strip())
                    if match:
                        name, version = match.groups()
                        dep = Dependency(
                            name=name,
                            version=version,
                            ecosystem='cargo',
                            direct=True
                        )
                        dependencies.append(dep)
        
        except Exception as e:
            print(f"Error parsing Cargo.toml: {e}")
        
        return dependencies
    def _parse_cargo_lock(self, file_path: Path) -> List[Dependency]:
        """Parse Cargo.lock for Rust dependencies."""
        dependencies = []
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Parse [[package]] entries
            packages = re.findall(r'\[\[package\]\]\nname\s*=\s*"([^"]+)"\nversion\s*=\s*"([^"]+)"', content)
            
            for name, version in packages:
                dep = Dependency(
                    name=name,
                    version=version,
                    ecosystem='cargo',
                    direct=False
                )
                dependencies.append(dep)
        
        except Exception as e:
            print(f"Error parsing Cargo.lock: {e}")
        
        return dependencies
    def _parse_gemfile(self, file_path: Path) -> List[Dependency]:
        """Parse Gemfile for Ruby dependencies."""
        dependencies = []
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Parse gem declarations
            gems = re.findall(r'gem\s+["\']([^"\']+)["\'](?:\s*,\s*["\']([^"\']+)["\'])?', content)
            
            for gem_info in gems:
                name = gem_info[0]
                version = gem_info[1] if len(gem_info) > 1 and gem_info[1] else ''
                
                dep = Dependency(
                    name=name,
                    version=version,
                    ecosystem='rubygems',
                    direct=True
                )
                dependencies.append(dep)
        
        except Exception as e:
            print(f"Error parsing Gemfile: {e}")
        
        return dependencies
    def _parse_gemfile_lock(self, file_path: Path) -> List[Dependency]:
        """Parse Gemfile.lock for Ruby dependencies."""
        dependencies = []
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Extract GEM section
            gem_section = re.search(r'GEM\s*\n(.*?)(?=\n\S|\Z)', content, re.DOTALL)
            if gem_section:
                specs = gem_section.group(1)
                gems = re.findall(r'\s+([a-zA-Z0-9_-]+)\s+\(([^)]+)\)', specs)
                
                for name, version in gems:
                    dep = Dependency(
                        name=name,
                        version=version,
                        ecosystem='rubygems',
                        direct=False
                    )
                    dependencies.append(dep)
        
        except Exception as e:
            print(f"Error parsing Gemfile.lock: {e}")
        
        return dependencies
