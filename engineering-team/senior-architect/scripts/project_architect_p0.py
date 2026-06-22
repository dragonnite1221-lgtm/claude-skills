# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from project_architect_base import *  # noqa: F403,E402


class PatternDetector:
    """Detects architectural patterns in a project."""

    # Pattern signatures
    PATTERNS = {
        'layered': {
            'indicators': ['controller', 'service', 'repository', 'dao', 'model', 'entity'],
            'structure': ['controllers', 'services', 'repositories', 'models'],
            'weight': 0,
        },
        'mvc': {
            'indicators': ['model', 'view', 'controller'],
            'structure': ['models', 'views', 'controllers'],
            'weight': 0,
        },
        'hexagonal': {
            'indicators': ['port', 'adapter', 'domain', 'infrastructure', 'application'],
            'structure': ['ports', 'adapters', 'domain', 'infrastructure'],
            'weight': 0,
        },
        'clean': {
            'indicators': ['entity', 'usecase', 'interface', 'framework', 'adapter'],
            'structure': ['entities', 'usecases', 'interfaces', 'frameworks'],
            'weight': 0,
        },
        'microservices': {
            'indicators': ['service', 'api', 'gateway', 'docker', 'kubernetes'],
            'structure': ['services', 'api-gateway', 'docker-compose'],
            'weight': 0,
        },
        'modular_monolith': {
            'indicators': ['module', 'feature', 'bounded'],
            'structure': ['modules', 'features'],
            'weight': 0,
        },
        'feature_based': {
            'indicators': ['feature', 'component', 'page'],
            'structure': ['features', 'components', 'pages'],
            'weight': 0,
        },
    }

    # Layer definitions for violation detection
    LAYER_HIERARCHY = {
        'presentation': ['controller', 'handler', 'view', 'page', 'component', 'ui', 'route'],
        'application': ['service', 'usecase', 'application', 'facade'],
        'domain': ['domain', 'entity', 'model', 'aggregate', 'valueobject'],
        'infrastructure': ['repository', 'dao', 'adapter', 'gateway', 'client', 'config'],
    }

    LAYER_ORDER = ['presentation', 'application', 'domain', 'infrastructure']

    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.directories: Set[str] = set()
        self.files: Dict[str, List[str]] = defaultdict(list)  # dir -> files
        self.detected_pattern: Optional[str] = None
        self.confidence: float = 0
        self.layer_assignments: Dict[str, str] = {}  # dir -> layer

    def scan(self) -> Dict:
        """Scan project and detect patterns."""
        self._scan_structure()
        self._detect_pattern()
        self._assign_layers()

        return {
            'detected_pattern': self.detected_pattern,
            'confidence': self.confidence,
            'directories': list(self.directories),
            'layer_assignments': self.layer_assignments,
            'pattern_scores': {p: d['weight'] for p, d in self.PATTERNS.items()},
        }

    def _scan_structure(self):
        """Scan directory structure."""
        ignore_dirs = {'.git', 'node_modules', '__pycache__', '.venv', 'venv',
                       'dist', 'build', '.next', 'coverage', '.pytest_cache'}

        for item in self.project_path.iterdir():
            if item.is_dir() and item.name not in ignore_dirs and not item.name.startswith('.'):
                self.directories.add(item.name.lower())

                # Scan files in directory
                try:
                    for f in item.rglob('*'):
                        if f.is_file():
                            self.files[item.name.lower()].append(f.name.lower())
                except PermissionError:
                    pass

    def _detect_pattern(self):
        """Detect the primary architectural pattern."""
        for pattern, config in self.PATTERNS.items():
            score = 0

            # Check directory structure
            for struct in config['structure']:
                if struct.lower() in self.directories:
                    score += 2

            # Check indicator presence in directory names
            for indicator in config['indicators']:
                for dir_name in self.directories:
                    if indicator in dir_name:
                        score += 1

            # Check file patterns
            all_files = [f for files in self.files.values() for f in files]
            for indicator in config['indicators']:
                matching_files = sum(1 for f in all_files if indicator in f)
                score += min(matching_files // 5, 3)  # Cap contribution

            config['weight'] = score

        # Find best match
        best_pattern = max(self.PATTERNS.items(), key=lambda x: x[1]['weight'])
        if best_pattern[1]['weight'] > 3:
            self.detected_pattern = best_pattern[0]
            max_possible = len(best_pattern[1]['structure']) * 2 + len(best_pattern[1]['indicators']) * 2
            self.confidence = min(100, int((best_pattern[1]['weight'] / max(max_possible, 1)) * 100))
        else:
            self.detected_pattern = 'unstructured'
            self.confidence = 0

    def _assign_layers(self):
        """Assign directories to architectural layers."""
        for dir_name in self.directories:
            for layer, indicators in self.LAYER_HIERARCHY.items():
                for indicator in indicators:
                    if indicator in dir_name:
                        self.layer_assignments[dir_name] = layer
                        break
                if dir_name in self.layer_assignments:
                    break

            if dir_name not in self.layer_assignments:
                self.layer_assignments[dir_name] = 'unknown'
