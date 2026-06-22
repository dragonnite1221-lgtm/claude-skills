# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from dependency_analyzer_base import *  # noqa: F403,E402


class DependencyAnalyzerMixin1:
    def _parse_poetry(self):
        """Parse pyproject.toml for Poetry dependencies."""
        toml_path = self.project_path / 'pyproject.toml'
        try:
            content = toml_path.read_text()

            # Simple TOML parsing for dependencies section
            in_deps = False
            in_dev_deps = False

            for line in content.split('\n'):
                line = line.strip()

                if line == '[tool.poetry.dependencies]':
                    in_deps = True
                    in_dev_deps = False
                    continue
                elif line == '[tool.poetry.dev-dependencies]' or \
                     line == '[tool.poetry.group.dev.dependencies]':
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
                        if name != 'python':
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
                'message': f"Failed to parse pyproject.toml: {e}"
            })
    def _parse_go(self):
        """Parse go.mod for Go dependencies."""
        mod_path = self.project_path / 'go.mod'
        try:
            content = mod_path.read_text()

            # Find require block
            in_require = False
            for line in content.split('\n'):
                line = line.strip()

                if line.startswith('require ('):
                    in_require = True
                    continue
                elif line == ')' and in_require:
                    in_require = False
                    continue
                elif line.startswith('require ') and '(' not in line:
                    # Single-line require
                    match = re.match(r'require\s+([^\s]+)\s+([^\s]+)', line)
                    if match:
                        self.direct_deps[match.group(1)] = match.group(2)
                    continue

                if in_require:
                    match = re.match(r'([^\s]+)\s+([^\s]+)', line)
                    if match:
                        self.direct_deps[match.group(1)] = match.group(2)

            if self.verbose:
                print(f"Found {len(self.direct_deps)} dependencies")

        except Exception as e:
            self.issues.append({
                'type': 'parse_error',
                'severity': 'error',
                'message': f"Failed to parse go.mod: {e}"
            })
