# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from script_tester_base import *  # noqa: F403,E402
from script_tester_p0 import ScriptTestResult  # noqa: F401,E501


class ScriptTesterMixin2:
    def _test_argparse_implementation(self, content: str, result: ScriptTestResult):
        """Test argparse implementation"""
        self.log_verbose("Testing argparse implementation...")
        
        try:
            tree = ast.parse(content)
            
            # Check for argparse import
            has_argparse_import = False
            has_parser_creation = False
            has_parse_args = False
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    if (isinstance(node, ast.Import) and 
                        any(alias.name == 'argparse' for alias in node.names)):
                        has_argparse_import = True
                    elif (isinstance(node, ast.ImportFrom) and 
                          node.module == 'argparse'):
                        has_argparse_import = True
                        
                elif isinstance(node, ast.Call):
                    # Check for ArgumentParser creation
                    if (isinstance(node.func, ast.Attribute) and
                        isinstance(node.func.value, ast.Name) and
                        node.func.value.id == 'argparse' and
                        node.func.attr == 'ArgumentParser'):
                        has_parser_creation = True
                        
                    # Check for parse_args call
                    if (isinstance(node.func, ast.Attribute) and
                        node.func.attr == 'parse_args'):
                        has_parse_args = True
                        
            argparse_score = sum([has_argparse_import, has_parser_creation, has_parse_args])
            
            if argparse_score == 3:
                result.add_test("argparse_implementation", True, "Complete argparse implementation found")
            elif argparse_score > 0:
                result.add_test("argparse_implementation", False, 
                               "Partial argparse implementation", 
                               {"missing_components": [
                                   comp for comp, present in [
                                       ("import", has_argparse_import),
                                       ("parser_creation", has_parser_creation),
                                       ("parse_args", has_parse_args)
                                   ] if not present
                               ]})
                result.add_warning("Incomplete argparse implementation")
            else:
                result.add_test("argparse_implementation", False, "No argparse implementation found")
                result.add_error("Script should use argparse for command-line arguments")
                
        except Exception as e:
            result.add_test("argparse_implementation", False, f"Error analyzing argparse: {str(e)}")
    def _test_main_guard(self, content: str, result: ScriptTestResult):
        """Test for if __name__ == '__main__' guard"""
        self.log_verbose("Testing main guard...")
        
        has_main_guard = 'if __name__ == "__main__"' in content or "if __name__ == '__main__'" in content
        
        if has_main_guard:
            result.add_test("main_guard", True, "Has proper main guard")
        else:
            result.add_test("main_guard", False, "Missing main guard")
            result.add_error("Script should have 'if __name__ == \"__main__\"' guard")
    def _test_script_execution(self, script_path: Path, result: ScriptTestResult):
        """Test basic script execution"""
        self.log_verbose("Testing script execution...")
        
        try:
            # Try to run the script with no arguments (should not crash immediately)
            process = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=script_path.parent
            )
            
            # Script might exit with error code if no args provided, but shouldn't crash
            if process.returncode in (0, 1, 2):  # 0=success, 1=general error, 2=misuse
                result.add_test("basic_execution", True, 
                               f"Script runs without crashing (exit code: {process.returncode})")
            else:
                result.add_test("basic_execution", False,
                               f"Script crashed with exit code {process.returncode}",
                               {"stdout": process.stdout, "stderr": process.stderr})
                               
        except subprocess.TimeoutExpired:
            result.add_test("basic_execution", False, 
                           f"Script execution timed out after {self.timeout} seconds")
            result.add_error(f"Script execution timeout ({self.timeout}s)")
            
        except Exception as e:
            result.add_test("basic_execution", False, f"Execution error: {str(e)}")
            result.add_error(f"Script execution failed: {str(e)}")
