# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from dependency_analyzer_base import *  # noqa: F403,E402


class DependencyAnalyzerMixin0:
    """Analyzes project dependencies and module coupling."""
    def __init__(self, project_path: Path, verbose: bool = False):
        self.project_path = project_path
        self.verbose = verbose

        # Results
        self.direct_deps: Dict[str, str] = {}  # name -> version
        self.dev_deps: Dict[str, str] = {}
        self.internal_modules: Dict[str, Set[str]] = defaultdict(set)  # module -> imports
        self.circular_deps: List[List[str]] = []
        self.coupling_score: float = 0
        self.issues: List[Dict] = []
        self.recommendations: List[str] = []
        self.package_manager: Optional[str] = None
    def analyze(self) -> Dict:
        """Run full dependency analysis."""
        self._detect_package_manager()
        self._parse_dependencies()
        self._scan_internal_modules()
        self._detect_circular_dependencies()
        self._calculate_coupling_score()
        self._generate_recommendations()

        return self._build_report()
    def _detect_package_manager(self):
        """Detect which package manager is used."""
        if (self.project_path / 'package.json').exists():
            self.package_manager = 'npm'
        elif (self.project_path / 'requirements.txt').exists():
            self.package_manager = 'pip'
        elif (self.project_path / 'pyproject.toml').exists():
            self.package_manager = 'poetry'
        elif (self.project_path / 'go.mod').exists():
            self.package_manager = 'go'
        elif (self.project_path / 'Cargo.toml').exists():
            self.package_manager = 'cargo'
        else:
            self.package_manager = 'unknown'

        if self.verbose:
            print(f"Detected package manager: {self.package_manager}")
    def _parse_dependencies(self):
        """Parse dependencies based on detected package manager."""
        parsers = {
            'npm': self._parse_npm,
            'pip': self._parse_pip,
            'poetry': self._parse_poetry,
            'go': self._parse_go,
            'cargo': self._parse_cargo,
        }

        parser = parsers.get(self.package_manager)
        if parser:
            parser()
    def _parse_npm(self):
        """Parse package.json for npm dependencies."""
        pkg_path = self.project_path / 'package.json'
        try:
            data = json.loads(pkg_path.read_text())

            # Direct dependencies
            for name, version in data.get('dependencies', {}).items():
                self.direct_deps[name] = self._clean_version(version)

            # Dev dependencies
            for name, version in data.get('devDependencies', {}).items():
                self.dev_deps[name] = self._clean_version(version)

            if self.verbose:
                print(f"Found {len(self.direct_deps)} direct deps, "
                      f"{len(self.dev_deps)} dev deps")

        except Exception as e:
            self.issues.append({
                'type': 'parse_error',
                'severity': 'error',
                'message': f"Failed to parse package.json: {e}"
            })
    def _parse_pip(self):
        """Parse requirements.txt for Python dependencies."""
        req_path = self.project_path / 'requirements.txt'
        try:
            content = req_path.read_text()
            for line in content.strip().split('\n'):
                line = line.strip()
                if not line or line.startswith('#') or line.startswith('-'):
                    continue

                # Parse name and version
                match = re.match(r'^([a-zA-Z0-9_-]+)(?:[=<>!~]+(.+))?', line)
                if match:
                    name = match.group(1)
                    version = match.group(2) or 'any'
                    self.direct_deps[name] = version

            if self.verbose:
                print(f"Found {len(self.direct_deps)} dependencies")

        except Exception as e:
            self.issues.append({
                'type': 'parse_error',
                'severity': 'error',
                'message': f"Failed to parse requirements.txt: {e}"
            })
