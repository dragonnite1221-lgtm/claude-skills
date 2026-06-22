# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from architecture_diagram_generator_base import *  # noqa: F403,E402


class ProjectScanner:
    """Scans project structure to detect components and relationships."""

    # Common architectural layer patterns
    LAYER_PATTERNS = {
        'presentation': ['controller', 'handler', 'view', 'page', 'component', 'ui'],
        'api': ['api', 'route', 'endpoint', 'rest', 'graphql'],
        'business': ['service', 'usecase', 'domain', 'logic', 'core'],
        'data': ['repository', 'dao', 'model', 'entity', 'schema', 'migration'],
        'infrastructure': ['config', 'util', 'helper', 'middleware', 'plugin'],
    }

    # File patterns for different technologies
    TECH_PATTERNS = {
        'react': ['jsx', 'tsx', 'package.json'],
        'vue': ['vue', 'nuxt.config'],
        'angular': ['component.ts', 'module.ts', 'angular.json'],
        'node': ['package.json', 'express', 'fastify'],
        'python': ['requirements.txt', 'pyproject.toml', 'setup.py'],
        'go': ['go.mod', 'go.sum'],
        'rust': ['Cargo.toml'],
        'java': ['pom.xml', 'build.gradle'],
        'docker': ['Dockerfile', 'docker-compose'],
        'kubernetes': ['deployment.yaml', 'service.yaml', 'k8s'],
    }

    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.components: Dict[str, Dict] = {}
        self.relationships: List[Tuple[str, str, str]] = []  # (from, to, type)
        self.layers: Dict[str, List[str]] = defaultdict(list)
        self.technologies: Set[str] = set()
        self.external_deps: Set[str] = set()

    def scan(self) -> Dict:
        """Scan the project and return structure information."""
        self._scan_directories()
        self._detect_technologies()
        self._detect_relationships()
        self._classify_layers()

        return {
            'components': self.components,
            'relationships': self.relationships,
            'layers': dict(self.layers),
            'technologies': list(self.technologies),
            'external_deps': list(self.external_deps),
        }

    def _scan_directories(self):
        """Scan directory structure for components."""
        ignore_dirs = {'.git', 'node_modules', '__pycache__', '.venv', 'venv',
                       'dist', 'build', '.next', '.nuxt', 'coverage', '.pytest_cache'}

        for item in self.project_path.iterdir():
            if item.is_dir() and item.name not in ignore_dirs and not item.name.startswith('.'):
                component_info = self._analyze_directory(item)
                if component_info['files'] > 0:
                    self.components[item.name] = component_info

    def _analyze_directory(self, dir_path: Path) -> Dict:
        """Analyze a directory to understand its role."""
        files = list(dir_path.rglob('*'))
        code_files = [f for f in files if f.is_file() and f.suffix in
                      ['.py', '.js', '.ts', '.jsx', '.tsx', '.go', '.rs', '.java', '.vue']]

        # Count imports/dependencies within the directory
        imports = set()
        for f in code_files[:50]:  # Limit to avoid large projects
            imports.update(self._extract_imports(f))

        return {
            'path': str(dir_path.relative_to(self.project_path)),
            'files': len(code_files),
            'imports': list(imports)[:20],  # Top 20 imports
            'type': self._guess_component_type(dir_path.name),
        }

    def _extract_imports(self, file_path: Path) -> Set[str]:
        """Extract import statements from a file."""
        imports = set()
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')

            # Python imports
            py_imports = re.findall(r'^(?:from|import)\s+([\w.]+)', content, re.MULTILINE)
            imports.update(py_imports)

            # JS/TS imports
            js_imports = re.findall(r'(?:import|require)\s*\(?[\'"]([^\'"\s]+)[\'"]', content)
            imports.update(js_imports)

            # Go imports
            go_imports = re.findall(r'import\s+(?:\(\s*)?["\']([^"\']+)["\']', content)
            imports.update(go_imports)

        except Exception:
            pass

        return imports

    def _guess_component_type(self, name: str) -> str:
        """Guess component type from directory name."""
        name_lower = name.lower()
        for layer, patterns in self.LAYER_PATTERNS.items():
            for pattern in patterns:
                if pattern in name_lower:
                    return layer
        return 'unknown'

    def _detect_technologies(self):
        """Detect technologies used in the project."""
        for tech, patterns in self.TECH_PATTERNS.items():
            for pattern in patterns:
                matches = list(self.project_path.rglob(f'*{pattern}*'))
                if matches:
                    self.technologies.add(tech)
                    break

        # Detect external dependencies from package files
        self._parse_package_json()
        self._parse_requirements_txt()
        self._parse_go_mod()

    def _parse_package_json(self):
        """Parse package.json for dependencies."""
        pkg_path = self.project_path / 'package.json'
        if pkg_path.exists():
            try:
                data = json.loads(pkg_path.read_text())
                deps = list(data.get('dependencies', {}).keys())[:10]
                self.external_deps.update(deps)
            except Exception:
                pass

    def _parse_requirements_txt(self):
        """Parse requirements.txt for dependencies."""
        req_path = self.project_path / 'requirements.txt'
        if req_path.exists():
            try:
                content = req_path.read_text()
                deps = re.findall(r'^([a-zA-Z0-9_-]+)', content, re.MULTILINE)[:10]
                self.external_deps.update(deps)
            except Exception:
                pass

    def _parse_go_mod(self):
        """Parse go.mod for dependencies."""
        mod_path = self.project_path / 'go.mod'
        if mod_path.exists():
            try:
                content = mod_path.read_text()
                deps = re.findall(r'^\s+([^\s]+)\s+v', content, re.MULTILINE)[:10]
                self.external_deps.update([d.split('/')[-1] for d in deps])
            except Exception:
                pass

    def _detect_relationships(self):
        """Detect relationships between components."""
        component_names = set(self.components.keys())

        for comp_name, comp_info in self.components.items():
            for imp in comp_info.get('imports', []):
                # Check if import references another component
                for other_comp in component_names:
                    if other_comp != comp_name and other_comp.lower() in imp.lower():
                        self.relationships.append((comp_name, other_comp, 'uses'))

    def _classify_layers(self):
        """Classify components into architectural layers."""
        for comp_name, comp_info in self.components.items():
            layer = comp_info.get('type', 'unknown')
            if layer != 'unknown':
                self.layers[layer].append(comp_name)
            else:
                self.layers['other'].append(comp_name)
