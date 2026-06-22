# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from skill_validator_base import *  # noqa: F403,E402


class SkillValidatorMixin3:
    def _validate_script_features(self, tree: ast.AST, script_name: str, content: str):
        """Validate required script features"""
        required_features = self._get_tier_requirement("features_required", ["argparse", "main_guard"])
        
        # Check for argparse usage
        if "argparse" in required_features:
            has_argparse = self._check_argparse_usage(tree)
            self.report.add_check(f"script_argparse_{script_name}", has_argparse,
                                 f"{'Uses' if has_argparse else 'Missing'} argparse in {script_name}", 1.0 if has_argparse else 0.0)
            if not has_argparse:
                self.report.add_error(f"{script_name} must use argparse for command-line arguments")
                
        # Check for main guard (accept both quote styles — both are valid Python)
        if "main_guard" in required_features:
            has_main_guard = bool(
                re.search(r'if\s+__name__\s*==\s*[\'"]__main__[\'"]', content)
            )
            self.report.add_check(f"script_main_guard_{script_name}", has_main_guard,
                                 f"{'Has' if has_main_guard else 'Missing'} main guard in {script_name}", 1.0 if has_main_guard else 0.0)
            if not has_main_guard:
                self.report.add_error(f"{script_name} must have 'if __name__ == \"__main__\"' guard")
                
        # Check for external imports (should only use stdlib)
        external_imports = self._check_external_imports(tree)
        if not external_imports:
            self.report.add_check(f"script_imports_{script_name}", True,
                                 f"{script_name} uses only standard library", 1.0)
        else:
            self.report.add_check(f"script_imports_{script_name}", False,
                                 f"{script_name} uses external imports: {', '.join(external_imports)}", 0.0)
            self.report.add_error(f"{script_name} uses external imports: {', '.join(external_imports)}")
    def _check_argparse_usage(self, tree: ast.AST) -> bool:
        """Check if the script uses argparse"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == 'argparse':
                        return True
            elif isinstance(node, ast.ImportFrom):
                if node.module == 'argparse':
                    return True
        return False
    def _check_external_imports(self, tree: ast.AST) -> List[str]:
        """Check for external (non-stdlib) imports"""
        # Simplified check - a more comprehensive solution would use a stdlib module list
        stdlib_modules = {
            'argparse', 'ast', 'json', 'os', 'sys', 'pathlib', 'datetime', 'typing',
            'collections', 're', 'math', 'random', 'itertools', 'functools', 'operator',
            'csv', 'sqlite3', 'urllib', 'http', 'html', 'xml', 'email', 'base64',
            'hashlib', 'hmac', 'secrets', 'tempfile', 'shutil', 'glob', 'fnmatch',
            'subprocess', 'threading', 'multiprocessing', 'queue', 'time', 'calendar',
            'zoneinfo', 'locale', 'gettext', 'logging', 'warnings', 'unittest',
            'doctest', 'pickle', 'copy', 'pprint', 'reprlib', 'enum', 'dataclasses',
            'contextlib', 'abc', 'atexit', 'traceback', 'gc', 'weakref', 'types',
            'copy', 'pprint', 'reprlib', 'enum', 'decimal', 'fractions', 'statistics',
            'cmath', 'platform', 'errno', 'io', 'codecs', 'unicodedata', 'stringprep',
            'textwrap', 'string', 'struct', 'difflib', 'heapq', 'bisect', 'array',
            'weakref', 'types', 'copyreg', 'uuid', 'mmap', 'ctypes'
        }
        
        external_imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_name = alias.name.split('.')[0]
                    if module_name not in stdlib_modules:
                        external_imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom) and node.module:
                module_name = node.module.split('.')[0]
                if module_name not in stdlib_modules:
                    external_imports.append(node.module)
                    
        return list(set(external_imports))
    def _validate_tier_compliance(self):
        """Validate overall tier compliance"""
        if not self.target_tier:
            return
            
        self.log_verbose(f"Validating {self.target_tier} tier compliance...")
        
        # This is a summary check - individual checks are done in other methods
        critical_checks = ["skill_md_exists", "min_scripts_count", "skill_md_length"]
        failed_critical = [check for check in critical_checks 
                          if check in self.report.checks and not self.report.checks[check]["passed"]]
                          
        if not failed_critical:
            self.report.add_check("tier_compliance", True,
                                 f"Meets {self.target_tier} tier requirements", 1.0)
        else:
            self.report.add_check("tier_compliance", False,
                                 f"Does not meet {self.target_tier} tier requirements", 0.0)
            self.report.add_error(f"Failed critical checks for {self.target_tier} tier: {', '.join(failed_critical)}")
    def _get_tier_requirement(self, requirement: str, default: Any) -> Any:
        """Get tier-specific requirement value"""
        if self.target_tier and self.target_tier in self.TIER_REQUIREMENTS:
            return self.TIER_REQUIREMENTS[self.target_tier].get(requirement, default)
        return default
