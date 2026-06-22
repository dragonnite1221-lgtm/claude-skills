# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from project_architect_base import *  # noqa: F403,E402


class LayerViolationDetector:
    """Detects architectural layer violations."""

    LAYER_ORDER = ['presentation', 'application', 'domain', 'infrastructure']

    # Valid dependency directions (key can depend on values)
    VALID_DEPENDENCIES = {
        'presentation': ['application', 'domain'],
        'application': ['domain', 'infrastructure'],
        'domain': [],  # Domain should not depend on other layers
        'infrastructure': ['domain'],
    }

    def __init__(self, project_path: Path, layer_assignments: Dict[str, str]):
        self.project_path = project_path
        self.layer_assignments = layer_assignments
        self.violations: List[Dict] = []

    def detect(self) -> List[Dict]:
        """Detect layer violations."""
        self._analyze_imports()
        return self.violations

    def _analyze_imports(self):
        """Analyze imports for layer violations."""
        extensions = ['.py', '.js', '.ts', '.jsx', '.tsx']
        ignore_dirs = {'.git', 'node_modules', '__pycache__', '.venv', 'venv',
                       'dist', 'build', '.next', 'coverage'}

        for ext in extensions:
            for file_path in self.project_path.rglob(f'*{ext}'):
                if any(ignored in file_path.parts for ignored in ignore_dirs):
                    continue

                try:
                    rel_path = file_path.relative_to(self.project_path)
                    if len(rel_path.parts) < 2:
                        continue

                    source_dir = rel_path.parts[0].lower()
                    source_layer = self.layer_assignments.get(source_dir)

                    if not source_layer or source_layer == 'unknown':
                        continue

                    # Extract imports
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    imports = self._extract_imports(content)

                    # Check each import for layer violations
                    for imp in imports:
                        target_dir = self._get_import_directory(imp)
                        if not target_dir:
                            continue

                        target_layer = self.layer_assignments.get(target_dir.lower())
                        if not target_layer or target_layer == 'unknown':
                            continue

                        if self._is_violation(source_layer, target_layer):
                            self.violations.append({
                                'type': 'layer_violation',
                                'severity': 'warning',
                                'file': str(rel_path),
                                'source_layer': source_layer,
                                'target_layer': target_layer,
                                'import': imp,
                                'message': f"{source_layer} layer should not depend on {target_layer} layer",
                            })

                except Exception:
                    pass

    def _extract_imports(self, content: str) -> List[str]:
        """Extract import statements."""
        imports = []

        # Python imports
        imports.extend(re.findall(r'^(?:from|import)\s+([\w.]+)', content, re.MULTILINE))

        # JS/TS imports
        imports.extend(re.findall(r'(?:import|require)\s*\(?[\'"]([^\'"\s]+)[\'"]', content))

        return imports

    def _get_import_directory(self, imp: str) -> Optional[str]:
        """Get the directory from an import path."""
        # Handle relative imports
        if imp.startswith('.'):
            return None  # Skip relative imports

        parts = imp.replace('@/', '').replace('~/', '').split('/')
        if parts:
            return parts[0].split('.')[0]
        return None

    def _is_violation(self, source_layer: str, target_layer: str) -> bool:
        """Check if the dependency is a violation."""
        if source_layer == target_layer:
            return False

        valid_deps = self.VALID_DEPENDENCIES.get(source_layer, [])
        return target_layer not in valid_deps and target_layer != source_layer
