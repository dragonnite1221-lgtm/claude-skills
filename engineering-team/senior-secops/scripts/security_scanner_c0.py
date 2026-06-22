# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from security_scanner_base import *  # noqa: F403,E402
from security_scanner_p0 import SecurityFinding  # noqa: F401,E501


class SecurityScannerMixin0:
    """Scan source code for security vulnerabilities."""
    SCAN_EXTENSIONS = {
        '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go',
        '.rb', '.php', '.cs', '.rs', '.swift', '.kt',
        '.yml', '.yaml', '.json', '.xml', '.env', '.conf', '.config'
    }
    SKIP_DIRS = {
        'node_modules', '.git', '__pycache__', '.venv', 'venv',
        'vendor', 'dist', 'build', '.next', 'coverage'
    }
    SECRET_PATTERNS = [
        (r'(?i)(api[_-]?key|apikey)\s*[:=]\s*["\']?([a-zA-Z0-9_\-]{20,})["\']?',
         'API Key', 'Hardcoded API key detected'),
        (r'(?i)(secret[_-]?key|secretkey)\s*[:=]\s*["\']?([a-zA-Z0-9_\-]{16,})["\']?',
         'Secret Key', 'Hardcoded secret key detected'),
        (r'(?i)(password|passwd|pwd)\s*[:=]\s*["\']([^"\']{4,})["\']',
         'Password', 'Hardcoded password detected'),
        (r'(?i)(aws[_-]?access[_-]?key[_-]?id)\s*[:=]\s*["\']?(AKIA[A-Z0-9]{16})["\']?',
         'AWS Access Key', 'Hardcoded AWS access key detected'),
        (r'(?i)(aws[_-]?secret[_-]?access[_-]?key)\s*[:=]\s*["\']?([a-zA-Z0-9/+=]{40})["\']?',
         'AWS Secret Key', 'Hardcoded AWS secret access key detected'),
        (r'ghp_[a-zA-Z0-9]{36}',
         'GitHub Token', 'GitHub personal access token detected'),
        (r'sk-[a-zA-Z0-9]{48}',
         'OpenAI API Key', 'OpenAI API key detected'),
        (r'-----BEGIN\s+(RSA|DSA|EC|OPENSSH)?\s*PRIVATE KEY-----',
         'Private Key', 'Private key detected in source code'),
    ]
    SQL_INJECTION_PATTERNS = [
        (r'execute\s*\(\s*["\']?\s*SELECT.*\+.*\+',
         'Dynamic SQL query with string concatenation'),
        (r'execute\s*\(\s*f["\']SELECT',
         'F-string SQL query (Python)'),
        (r'cursor\.execute\s*\(\s*["\'].*%s.*%\s*\(',
         'Unsafe string formatting in SQL'),
        (r'query\s*\(\s*[`"\']SELECT.*\$\{',
         'Template literal SQL injection (JavaScript)'),
        (r'\.query\s*\(\s*["\'].*\+.*\+',
         'String concatenation in SQL query'),
    ]
    XSS_PATTERNS = [
        (r'innerHTML\s*=\s*[^;]+(?:user|input|param|query)',
         'User input assigned to innerHTML'),
        (r'document\.write\s*\([^;]*(?:user|input|param|query)',
         'User input in document.write'),
        (r'\.html\s*\(\s*[^)]*(?:user|input|param|query)',
         'User input in jQuery .html()'),
        (r'dangerouslySetInnerHTML',
         'React dangerouslySetInnerHTML usage'),
        (r'\|safe\s*}}',
         'Django safe filter may disable escaping'),
    ]
    COMMAND_INJECTION_PATTERNS = [
        (r'subprocess\.(?:call|run|Popen)\s*\([^)]*shell\s*=\s*True',
         'Subprocess with shell=True'),
        (r'exec\s*\(\s*[^)]*(?:user|input|param|request)',
         'exec() with potential user input'),
        (r'eval\s*\(\s*[^)]*(?:user|input|param|request)',
         'eval() with potential user input'),
    ]
    PATH_TRAVERSAL_PATTERNS = [
        (r'open\s*\(\s*[^)]*(?:user|input|param|request)',
         'File open with potential user input'),
        (r'readFile\s*\(\s*[^)]*(?:user|input|param|req\.|query)',
         'File read with potential user input'),
        (r'path\.join\s*\([^)]*(?:user|input|param|req\.|query)',
         'Path.join with user input without validation'),
    ]
    def __init__(
        self,
        target_path: str,
        severity_threshold: str = "low",
        verbose: bool = False
    ):
        """
        Initialize the security scanner.

        Args:
            target_path: Directory or file to scan
            severity_threshold: Minimum severity to report (critical, high, medium, low)
            verbose: Enable verbose output
        """
        self.target_path = Path(target_path)
        self.severity_threshold = severity_threshold
        self.verbose = verbose
        self.findings: List[SecurityFinding] = []
        self.files_scanned = 0
        self.severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3, 'info': 4}
    def scan(self) -> Dict:
        """
        Run all security scans.

        Returns:
            Dict with scan results and findings
        """
        print(f"Security Scanner - Scanning: {self.target_path}")
        print(f"Severity threshold: {self.severity_threshold}")
        print()

        if not self.target_path.exists():
            return {"status": "error", "message": f"Path not found: {self.target_path}"}

        start_time = datetime.now()

        # Collect files to scan
        files_to_scan = self._collect_files()
        print(f"Files to scan: {len(files_to_scan)}")

        # Run scans
        for file_path in files_to_scan:
            self._scan_file(file_path)
            self.files_scanned += 1

        # Filter by severity threshold
        threshold_level = self.severity_order.get(self.severity_threshold, 3)
        filtered_findings = [
            f for f in self.findings
            if self.severity_order.get(f.severity, 3) <= threshold_level
        ]

        end_time = datetime.now()
        scan_duration = (end_time - start_time).total_seconds()

        # Group findings by severity
        severity_counts = {}
        for finding in filtered_findings:
            severity_counts[finding.severity] = severity_counts.get(finding.severity, 0) + 1

        result = {
            "status": "completed",
            "target": str(self.target_path),
            "files_scanned": self.files_scanned,
            "scan_duration_seconds": round(scan_duration, 2),
            "total_findings": len(filtered_findings),
            "severity_counts": severity_counts,
            "findings": [asdict(f) for f in filtered_findings]
        }

        self._print_summary(result)

        return result
    def _collect_files(self) -> List[Path]:
        """Collect files to scan."""
        files = []

        if self.target_path.is_file():
            return [self.target_path]

        for root, dirs, filenames in os.walk(self.target_path):
            # Skip directories
            dirs[:] = [d for d in dirs if d not in self.SKIP_DIRS]

            for filename in filenames:
                file_path = Path(root) / filename
                if file_path.suffix.lower() in self.SCAN_EXTENSIONS:
                    files.append(file_path)

        return files
