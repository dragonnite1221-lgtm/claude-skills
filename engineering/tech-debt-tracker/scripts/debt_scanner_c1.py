# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from debt_scanner_base import *  # noqa: F403,E402
from debt_scanner_p0 import PythonASTAnalyzer  # noqa: F401,E501


class DebtScannerMixin1:
    def _should_ignore(self, name: str) -> bool:
        """Check if file/directory should be ignored."""
        for pattern in self.config["ignore_patterns"]:
            if "*" in pattern:
                if re.match(pattern.replace("*", ".*"), name):
                    return True
            elif pattern in name:
                return True
        return False
    def _scan_file(self, file_path: str, relative_path: str):
        """Scan a single file for tech debt."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.splitlines()
        except Exception as e:
            print(f"Cannot read {relative_path}: {e}")
            return
        
        file_ext = Path(file_path).suffix.lower()
        file_info = {
            "path": relative_path,
            "lines": len(lines),
            "size_kb": os.path.getsize(file_path) / 1024,
            "language": self._detect_language(file_ext),
            "debt_count": 0
        }
        
        self.stats["files_scanned"] += 1
        self.stats["total_lines"] += len(lines)
        
        # File size debt
        if len(lines) > self.config["max_file_size_lines"]:
            self._add_debt_item(
                "large_file",
                f"File is too large: {len(lines)} lines",
                relative_path,
                "medium",
                {"lines": len(lines), "recommended_max": self.config["max_file_size_lines"]}
            )
            file_info["debt_count"] += 1
        
        # Language-specific analysis
        if file_info["language"] == "python" and file_ext == ".py":
            self._scan_python_file(relative_path, content, lines)
        else:
            self._scan_generic_file(relative_path, content, lines, file_info["language"])
        
        # Common patterns for all languages
        self._scan_common_patterns(relative_path, content, lines)
        
        self.file_stats[relative_path] = file_info
    def _detect_language(self, file_ext: str) -> str:
        """Detect programming language from file extension."""
        for lang, extensions in self.config["file_extensions"].items():
            if file_ext in extensions:
                return lang
        return "unknown"
    def _scan_python_file(self, file_path: str, content: str, lines: List[str]):
        """Scan Python files using AST parsing."""
        try:
            tree = ast.parse(content)
            analyzer = PythonASTAnalyzer(self.config)
            debt_items = analyzer.analyze(tree, file_path, lines)
            self.debt_items.extend(debt_items)
            self.stats["python_files"] += 1
        except SyntaxError as e:
            self._add_debt_item(
                "syntax_error",
                f"Python syntax error: {e}",
                file_path,
                "high",
                {"line": e.lineno, "error": str(e)}
            )
    def _scan_generic_file(self, file_path: str, content: str, lines: List[str], language: str):
        """Scan non-Python files using pattern matching."""
        # Detect long lines
        for i, line in enumerate(lines):
            if len(line) > 120:
                self._add_debt_item(
                    "long_line",
                    f"Line too long: {len(line)} characters",
                    file_path,
                    "low",
                    {"line_number": i + 1, "length": len(line)}
                )
        
        # Detect deep nesting (approximate)
        for i, line in enumerate(lines):
            indent_level = len(line) - len(line.lstrip())
            if language in ["python"]:
                indent_level = indent_level // 4  # Python uses 4-space indents
            elif language in ["javascript", "java", "csharp", "cpp"]:
                # Count braces for brace-based languages
                brace_level = content[:content.find('\n'.join(lines[:i+1]))].count('{') - content[:content.find('\n'.join(lines[:i+1]))].count('}')
                if brace_level > self.config["max_nesting_depth"]:
                    self._add_debt_item(
                        "deep_nesting",
                        f"Deep nesting detected: {brace_level} levels",
                        file_path,
                        "medium",
                        {"line_number": i + 1, "nesting_level": brace_level}
                    )
