# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from dependency_analyzer_base import *  # noqa: F403,E402


class DependencyAnalyzerMixin2:
    def _parse_cargo(self):
        """Parse Cargo.toml for Rust dependencies."""
        cargo_path = self.project_path / 'Cargo.toml'
        try:
            content = cargo_path.read_text()

            in_deps = False
            in_dev_deps = False

            for line in content.split('\n'):
                line = line.strip()

                if line == '[dependencies]':
                    in_deps = True
                    in_dev_deps = False
                    continue
                elif line == '[dev-dependencies]':
                    in_deps = False
                    in_dev_deps = True
                    continue
                elif line.startswith('['):
                    in_deps = False
                    in_dev_deps = False
                    continue

                if (in_deps or in_dev_deps) and '=' in line:
                    match = re.match(r'^([a-zA-Z0-9_-]+)\s*=\s*["\']?([^"\']+)', line)
                    if match:
                        name = match.group(1)
                        version = match.group(2)
                        if in_deps:
                            self.direct_deps[name] = version
                        else:
                            self.dev_deps[name] = version

            if self.verbose:
                print(f"Found {len(self.direct_deps)} direct deps, "
                      f"{len(self.dev_deps)} dev deps")

        except Exception as e:
            self.issues.append({
                'type': 'parse_error',
                'severity': 'error',
                'message': f"Failed to parse Cargo.toml: {e}"
            })
    def _clean_version(self, version: str) -> str:
        """Clean version string."""
        return version.lstrip('^~>=<!')
    def _scan_internal_modules(self):
        """Scan internal module imports for coupling analysis."""
        ignore_dirs = {'.git', 'node_modules', '__pycache__', '.venv', 'venv',
                       'dist', 'build', '.next', 'coverage'}

        # Find all code files
        extensions = ['.py', '.js', '.ts', '.jsx', '.tsx', '.go', '.rs']

        for ext in extensions:
            for file_path in self.project_path.rglob(f'*{ext}'):
                # Skip ignored directories
                if any(ignored in file_path.parts for ignored in ignore_dirs):
                    continue

                # Get module name (directory relative to project root)
                try:
                    rel_path = file_path.relative_to(self.project_path)
                    module = rel_path.parts[0] if len(rel_path.parts) > 1 else 'root'

                    # Extract imports
                    imports = self._extract_imports(file_path)
                    self.internal_modules[module].update(imports)

                except Exception:
                    continue

        if self.verbose:
            print(f"Scanned {len(self.internal_modules)} internal modules")
    def _extract_imports(self, file_path: Path) -> Set[str]:
        """Extract import statements from a file."""
        imports = set()
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')

            # Python imports
            for match in re.finditer(r'^(?:from|import)\s+([\w.]+)', content, re.MULTILINE):
                imports.add(match.group(1).split('.')[0])

            # JS/TS imports
            for match in re.finditer(r'(?:import|require)\s*\(?[\'"]([^\'"\s]+)[\'"]', content):
                imp = match.group(1)
                if imp.startswith('.') or imp.startswith('@/') or imp.startswith('~/'):
                    # Relative import - extract first path component
                    parts = imp.lstrip('./~@').split('/')
                    if parts:
                        imports.add(parts[0])

        except Exception:
            pass

        return imports
