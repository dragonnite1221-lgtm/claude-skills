# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from debt_scanner_base import *  # noqa: F403,E402


class DebtScannerMixin0:
    """Main scanner class for detecting technical debt in codebases."""
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = self._load_default_config()
        if config:
            self.config.update(config)
        
        self.debt_items = []
        self.stats = defaultdict(int)
        self.file_stats = {}
        
        # Compile regex patterns for performance
        self._compile_patterns()
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration for debt detection."""
        return {
            "max_function_length": 50,
            "max_complexity": 10,
            "max_nesting_depth": 4,
            "max_file_size_lines": 500,
            "min_duplicate_lines": 3,
            "ignore_patterns": [
                "*.pyc", "__pycache__", ".git", ".svn", "node_modules",
                "build", "dist", "*.min.js", "*.map"
            ],
            "file_extensions": {
                "python": [".py"],
                "javascript": [".js", ".jsx", ".ts", ".tsx"],
                "java": [".java"],
                "csharp": [".cs"],
                "cpp": [".cpp", ".cc", ".cxx", ".c", ".h", ".hpp"],
                "ruby": [".rb"],
                "php": [".php"],
                "go": [".go"],
                "rust": [".rs"],
                "kotlin": [".kt"]
            },
            "comment_patterns": {
                "todo": r"(?i)(TODO|FIXME|HACK|XXX|BUG)[\s:]*(.+)",
                "commented_code": r"^\s*#.*[=(){}\[\];].*",
                "magic_numbers": r"\b\d{2,}\b",
                "long_strings": r'["\'](.{100,})["\']'
            },
            "severity_weights": {
                "critical": 10,
                "high": 7,
                "medium": 5,
                "low": 2,
                "info": 1
            }
        }
    def _compile_patterns(self):
        """Compile regex patterns for better performance."""
        self.comment_regexes = {}
        for name, pattern in self.config["comment_patterns"].items():
            self.comment_regexes[name] = re.compile(pattern)
        
        # Common code smells patterns
        self.smell_patterns = {
            "empty_catch": re.compile(r"except[^:]*:\s*pass\s*$", re.MULTILINE),
            "print_debug": re.compile(r"print\s*\([^)]*debug[^)]*\)", re.IGNORECASE),
            "hardcoded_paths": re.compile(r'["\'][/\\][^"\']*[/\\][^"\']*["\']'),
            "sql_injection_risk": re.compile(r'["\'].*%s.*["\'].*execute', re.IGNORECASE),
        }
    def scan_directory(self, directory: str) -> Dict[str, Any]:
        """
        Scan a directory for tech debt.
        
        Args:
            directory: Path to the directory to scan
            
        Returns:
            Dictionary containing debt inventory and statistics
        """
        directory_path = Path(directory)
        if not directory_path.exists():
            raise ValueError(f"Directory does not exist: {directory}")
        
        print(f"Scanning directory: {directory}")
        print("=" * 50)
        
        # Reset state
        self.debt_items = []
        self.stats = defaultdict(int)
        self.file_stats = {}
        
        # Walk through directory
        for root, dirs, files in os.walk(directory):
            # Filter out ignored directories
            dirs[:] = [d for d in dirs if not self._should_ignore(d)]
            
            for file in files:
                if self._should_ignore(file):
                    continue
                
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, directory)
                
                try:
                    self._scan_file(file_path, relative_path)
                except Exception as e:
                    print(f"Error scanning {relative_path}: {e}")
                    self.stats["scan_errors"] += 1
        
        # Post-process results
        self._detect_duplicates(directory)
        self._calculate_priorities()
        
        return self._generate_report(directory)
