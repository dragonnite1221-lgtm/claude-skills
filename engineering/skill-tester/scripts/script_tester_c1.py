# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from script_tester_base import *  # noqa: F403,E402
from script_tester_p0 import ScriptTestResult  # noqa: F401,E501


class ScriptTesterMixin1:
    def _test_syntax(self, content: str, result: ScriptTestResult):
        """Test Python syntax validity"""
        self.log_verbose("Testing syntax...")
        
        try:
            ast.parse(content)
            result.add_test("syntax_valid", True, "Python syntax is valid")
        except SyntaxError as e:
            result.add_test("syntax_valid", False, f"Syntax error: {str(e)}", 
                           {"error": str(e), "line": getattr(e, 'lineno', 'unknown')})
            result.add_error(f"Syntax error: {str(e)}")
    def _test_imports(self, content: str, result: ScriptTestResult):
        """Test import statements for external dependencies"""
        self.log_verbose("Testing imports...")
        
        try:
            tree = ast.parse(content)
            external_imports = self._find_external_imports(tree)
            
            if not external_imports:
                result.add_test("imports_valid", True, "Uses only standard library imports")
            else:
                result.add_test("imports_valid", False, 
                               f"Uses external imports: {', '.join(external_imports)}",
                               {"external_imports": external_imports})
                result.add_error(f"External imports detected: {', '.join(external_imports)}")
                
        except Exception as e:
            result.add_test("imports_valid", False, f"Error analyzing imports: {str(e)}")
    def _find_external_imports(self, tree: ast.AST) -> List[str]:
        """Find external (non-stdlib) imports"""
        # Comprehensive standard library module list
        stdlib_modules = {
            # Built-in modules
            'argparse', 'ast', 'json', 'os', 'sys', 'pathlib', 'datetime', 'typing',
            'collections', 're', 'math', 'random', 'itertools', 'functools', 'operator',
            'csv', 'sqlite3', 'urllib', 'http', 'html', 'xml', 'email', 'base64',
            'hashlib', 'hmac', 'secrets', 'tempfile', 'shutil', 'glob', 'fnmatch',
            'subprocess', 'threading', 'multiprocessing', 'queue', 'time', 'calendar',
            'locale', 'gettext', 'logging', 'warnings', 'unittest', 'doctest',
            'pickle', 'copy', 'pprint', 'reprlib', 'enum', 'dataclasses',
            'contextlib', 'abc', 'atexit', 'traceback', 'gc', 'weakref', 'types',
            'decimal', 'fractions', 'statistics', 'cmath', 'platform', 'errno',
            'io', 'codecs', 'unicodedata', 'stringprep', 'textwrap', 'string',
            'struct', 'difflib', 'heapq', 'bisect', 'array', 'uuid', 'mmap',
            'ctypes', 'winreg', 'msvcrt', 'winsound', 'posix', 'pwd', 'grp',
            'crypt', 'termios', 'tty', 'pty', 'fcntl', 'resource', 'nis',
            'syslog', 'signal', 'socket', 'ssl', 'select', 'selectors',
            'asyncio', 'asynchat', 'asyncore', 'netrc', 'xdrlib', 'plistlib',
            'mailbox', 'mimetypes', 'encodings', 'pkgutil', 'modulefinder',
            'runpy', 'importlib', 'imp', 'zipimport', 'zipfile', 'tarfile',
            'gzip', 'bz2', 'lzma', 'zlib', 'binascii', 'quopri', 'uu',
            'configparser', 'netrc', 'xdrlib', 'plistlib', 'token', 'tokenize',
            'keyword', 'heapq', 'bisect', 'array', 'weakref', 'types',
            'copyreg', 'shelve', 'marshal', 'dbm', 'sqlite3', 'zoneinfo'
        }
        
        external_imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_name = alias.name.split('.')[0]
                    if module_name not in stdlib_modules and not module_name.startswith('_'):
                        external_imports.append(alias.name)
                        
            elif isinstance(node, ast.ImportFrom) and node.module:
                module_name = node.module.split('.')[0]
                if module_name not in stdlib_modules and not module_name.startswith('_'):
                    external_imports.append(node.module)
                    
        return list(set(external_imports))
