# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from security_scanner_base import *  # noqa: F403,E402
from security_scanner_p0 import SecurityFinding  # noqa: F401,E501


class SecurityScannerMixin1:
    def _scan_file(self, file_path: Path):
        """Scan a single file for security issues."""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            lines = content.split('\n')

            relative_path = str(file_path.relative_to(self.target_path) if self.target_path.is_dir() else file_path.name)

            # Scan for secrets
            self._scan_patterns(
                lines, relative_path,
                self.SECRET_PATTERNS,
                'secrets',
                'Hardcoded Secret',
                'critical'
            )

            # Scan for SQL injection
            self._scan_patterns(
                lines, relative_path,
                [(p[0], p[1]) for p in self.SQL_INJECTION_PATTERNS],
                'injection',
                'SQL Injection',
                'high'
            )

            # Scan for XSS
            self._scan_patterns(
                lines, relative_path,
                [(p[0], p[1]) for p in self.XSS_PATTERNS],
                'xss',
                'Cross-Site Scripting (XSS)',
                'high'
            )

            # Scan for command injection
            self._scan_patterns(
                lines, relative_path,
                [(p[0], p[1]) for p in self.COMMAND_INJECTION_PATTERNS],
                'injection',
                'Command Injection',
                'critical'
            )

            # Scan for path traversal
            self._scan_patterns(
                lines, relative_path,
                [(p[0], p[1]) for p in self.PATH_TRAVERSAL_PATTERNS],
                'path-traversal',
                'Path Traversal',
                'medium'
            )

            if self.verbose:
                print(f"  Scanned: {relative_path}")

        except Exception as e:
            if self.verbose:
                print(f"  Error scanning {file_path}: {e}")
    def _scan_patterns(
        self,
        lines: List[str],
        file_path: str,
        patterns: List[Tuple],
        category: str,
        title: str,
        default_severity: str
    ):
        """Scan lines for patterns."""
        for line_num, line in enumerate(lines, 1):
            for pattern_tuple in patterns:
                pattern = pattern_tuple[0]
                description = pattern_tuple[1] if len(pattern_tuple) > 1 else title

                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    # Check for false positives (comments, test files)
                    if self._is_false_positive(line, file_path):
                        continue

                    # Determine severity based on context
                    severity = self._calculate_severity(
                        default_severity,
                        file_path,
                        category
                    )

                    finding = SecurityFinding(
                        rule_id=f"{category}-{len(self.findings) + 1:04d}",
                        severity=severity,
                        category=category,
                        title=title,
                        description=description,
                        file_path=file_path,
                        line_number=line_num,
                        code_snippet=line.strip()[:100],
                        recommendation=self._get_recommendation(category)
                    )

                    self.findings.append(finding)
