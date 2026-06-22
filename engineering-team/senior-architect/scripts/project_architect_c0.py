# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from project_architect_base import *  # noqa: F403,E402


class CodeAnalyzerMixin0:
    """Analyzes code for architectural issues."""
    MAX_FILE_LINES = 500
    MAX_CLASS_LINES = 300
    MAX_FUNCTION_LINES = 50
    MAX_IMPORTS_PER_FILE = 30
    def __init__(self, project_path: Path, verbose: bool = False):
        self.project_path = project_path
        self.verbose = verbose
        self.issues: List[Dict] = []
        self.metrics: Dict = {}
    def analyze(self) -> Dict:
        """Run code analysis."""
        self._analyze_file_sizes()
        self._analyze_imports()
        self._detect_god_classes()
        self._check_naming_conventions()

        return {
            'issues': self.issues,
            'metrics': self.metrics,
        }
    def _analyze_file_sizes(self):
        """Check for oversized files."""
        extensions = ['.py', '.js', '.ts', '.jsx', '.tsx', '.go', '.rs', '.java']
        large_files = []
        total_lines = 0
        file_count = 0

        ignore_dirs = {'.git', 'node_modules', '__pycache__', '.venv', 'venv',
                       'dist', 'build', '.next', 'coverage'}

        for ext in extensions:
            for file_path in self.project_path.rglob(f'*{ext}'):
                if any(ignored in file_path.parts for ignored in ignore_dirs):
                    continue

                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    lines = len(content.split('\n'))
                    total_lines += lines
                    file_count += 1

                    if lines > self.MAX_FILE_LINES:
                        large_files.append({
                            'path': str(file_path.relative_to(self.project_path)),
                            'lines': lines,
                        })
                        self.issues.append({
                            'type': 'large_file',
                            'severity': 'warning',
                            'file': str(file_path.relative_to(self.project_path)),
                            'message': f"File has {lines} lines (threshold: {self.MAX_FILE_LINES})",
                            'suggestion': "Consider splitting into smaller, focused modules",
                        })
                except Exception:
                    pass

        self.metrics['total_lines'] = total_lines
        self.metrics['file_count'] = file_count
        self.metrics['avg_file_lines'] = total_lines // file_count if file_count > 0 else 0
        self.metrics['large_files'] = large_files
    def _analyze_imports(self):
        """Analyze import patterns."""
        extensions = ['.py', '.js', '.ts', '.jsx', '.tsx']
        high_import_files = []

        ignore_dirs = {'.git', 'node_modules', '__pycache__', '.venv', 'venv',
                       'dist', 'build', '.next', 'coverage'}

        for ext in extensions:
            for file_path in self.project_path.rglob(f'*{ext}'):
                if any(ignored in file_path.parts for ignored in ignore_dirs):
                    continue

                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')

                    # Count imports
                    py_imports = len(re.findall(r'^(?:from|import)\s+', content, re.MULTILINE))
                    js_imports = len(re.findall(r'^import\s+', content, re.MULTILINE))
                    imports = py_imports + js_imports

                    if imports > self.MAX_IMPORTS_PER_FILE:
                        high_import_files.append({
                            'path': str(file_path.relative_to(self.project_path)),
                            'imports': imports,
                        })
                        self.issues.append({
                            'type': 'high_imports',
                            'severity': 'info',
                            'file': str(file_path.relative_to(self.project_path)),
                            'message': f"File has {imports} imports (threshold: {self.MAX_IMPORTS_PER_FILE})",
                            'suggestion': "Consider if all imports are necessary or if the file has too many responsibilities",
                        })
                except Exception:
                    pass

        self.metrics['high_import_files'] = high_import_files
