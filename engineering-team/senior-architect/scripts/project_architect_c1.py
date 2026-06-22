# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from project_architect_base import *  # noqa: F403,E402


class CodeAnalyzerMixin1:
    def _detect_god_classes(self):
        """Detect potential god classes (oversized classes)."""
        extensions = ['.py', '.js', '.ts', '.java']
        god_classes = []

        ignore_dirs = {'.git', 'node_modules', '__pycache__', '.venv', 'venv',
                       'dist', 'build', '.next', 'coverage'}

        for ext in extensions:
            for file_path in self.project_path.rglob(f'*{ext}'):
                if any(ignored in file_path.parts for ignored in ignore_dirs):
                    continue

                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    lines = content.split('\n')

                    # Simple class detection
                    class_pattern = r'^\s*(?:export\s+)?(?:abstract\s+)?class\s+(\w+)'
                    in_class = False
                    class_name = None
                    class_start = 0
                    brace_count = 0

                    for i, line in enumerate(lines):
                        match = re.match(class_pattern, line)
                        if match:
                            if in_class and class_name:
                                # End previous class
                                class_lines = i - class_start
                                if class_lines > self.MAX_CLASS_LINES:
                                    god_classes.append({
                                        'file': str(file_path.relative_to(self.project_path)),
                                        'class': class_name,
                                        'lines': class_lines,
                                    })
                            class_name = match.group(1)
                            class_start = i
                            in_class = True

                    # Check last class
                    if in_class and class_name:
                        class_lines = len(lines) - class_start
                        if class_lines > self.MAX_CLASS_LINES:
                            god_classes.append({
                                'file': str(file_path.relative_to(self.project_path)),
                                'class': class_name,
                                'lines': class_lines,
                            })
                            self.issues.append({
                                'type': 'god_class',
                                'severity': 'warning',
                                'file': str(file_path.relative_to(self.project_path)),
                                'message': f"Class '{class_name}' has ~{class_lines} lines (threshold: {self.MAX_CLASS_LINES})",
                                'suggestion': "Consider applying Single Responsibility Principle and splitting into smaller classes",
                            })

                except Exception:
                    pass

        self.metrics['god_classes'] = god_classes
    def _check_naming_conventions(self):
        """Check for naming convention issues."""
        ignore_dirs = {'.git', 'node_modules', '__pycache__', '.venv', 'venv',
                       'dist', 'build', '.next', 'coverage'}

        naming_issues = []

        # Check directory naming
        for dir_path in self.project_path.rglob('*'):
            if not dir_path.is_dir():
                continue
            if any(ignored in dir_path.parts for ignored in ignore_dirs):
                continue

            dir_name = dir_path.name
            # Check for mixed case in directories (should be kebab-case or snake_case)
            if re.search(r'[A-Z]', dir_name) and '-' not in dir_name and '_' not in dir_name:
                rel_path = str(dir_path.relative_to(self.project_path))
                if len(rel_path.split('/')) <= 3:  # Only check top-level dirs
                    naming_issues.append({
                        'type': 'directory',
                        'path': rel_path,
                        'issue': 'PascalCase directory name',
                    })

        if naming_issues:
            self.issues.append({
                'type': 'naming_convention',
                'severity': 'info',
                'message': f"Found {len(naming_issues)} naming convention inconsistencies",
                'details': naming_issues[:5],  # Show first 5
            })

        self.metrics['naming_issues'] = naming_issues
