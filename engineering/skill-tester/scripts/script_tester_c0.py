# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from script_tester_base import *  # noqa: F403,E402
from script_tester_p0 import ScriptTestResult, TestSuite  # noqa: F401,E501


class ScriptTesterMixin0:
    """Main script testing engine"""
    def __init__(self, skill_path: str, timeout: int = 30, verbose: bool = False):
        self.skill_path = Path(skill_path).resolve()
        self.timeout = timeout
        self.verbose = verbose
        self.test_suite = TestSuite(str(self.skill_path))
    def log_verbose(self, message: str):
        """Log verbose message if verbose mode enabled"""
        if self.verbose:
            print(f"[VERBOSE] {message}", file=sys.stderr)
    def test_all_scripts(self) -> TestSuite:
        """Main entry point - test all scripts in the skill"""
        try:
            self.log_verbose(f"Starting script testing for {self.skill_path}")
            
            # Check if skill path exists
            if not self.skill_path.exists():
                self.test_suite.add_global_error(f"Skill path does not exist: {self.skill_path}")
                return self.test_suite
                
            scripts_dir = self.skill_path / "scripts"
            if not scripts_dir.exists():
                self.test_suite.add_global_error("No scripts directory found")
                return self.test_suite
                
            # Find all Python scripts
            python_files = list(scripts_dir.glob("*.py"))
            if not python_files:
                self.test_suite.add_global_error("No Python scripts found in scripts directory")
                return self.test_suite
                
            self.log_verbose(f"Found {len(python_files)} Python scripts to test")
            
            # Test each script
            for script_path in python_files:
                try:
                    result = self.test_single_script(script_path)
                    self.test_suite.add_script_result(result)
                except Exception as e:
                    # Create a failed result for the script
                    result = ScriptTestResult(str(script_path))
                    result.add_error(f"Failed to test script: {str(e)}")
                    result.overall_status = "FAIL"
                    self.test_suite.add_script_result(result)
                    
            # Calculate summary
            self.test_suite.calculate_summary()
            
        except Exception as e:
            self.test_suite.add_global_error(f"Testing failed with exception: {str(e)}")
            
        return self.test_suite
    def test_single_script(self, script_path: Path) -> ScriptTestResult:
        """Test a single Python script comprehensively"""
        result = ScriptTestResult(str(script_path))
        start_time = time.time()
        
        try:
            self.log_verbose(f"Testing script: {script_path.name}")
            
            # Read script content
            try:
                content = script_path.read_text(encoding='utf-8')
            except Exception as e:
                result.add_test("file_readable", False, f"Cannot read file: {str(e)}")
                result.add_error(f"Cannot read script file: {str(e)}")
                result.overall_status = "FAIL"
                return result
                
            result.add_test("file_readable", True, "Script file is readable")
            
            # Test 1: Syntax validation
            self._test_syntax(content, result)
            
            # Test 2: Import validation  
            self._test_imports(content, result)
            
            # Test 3: Argparse validation
            self._test_argparse_implementation(content, result)
            
            # Test 4: Main guard validation
            self._test_main_guard(content, result)
            
            # Test 5: Runtime execution tests
            if result.tests.get("syntax_valid", {}).get("passed", False):
                self._test_script_execution(script_path, result)
                
            # Test 6: Help functionality
            if result.tests.get("syntax_valid", {}).get("passed", False):
                self._test_help_functionality(script_path, result)
                
            # Test 7: Sample data processing (if available)
            self._test_sample_data_processing(script_path, result)
            
            # Test 8: Output format validation
            self._test_output_formats(script_path, result)
            
        except Exception as e:
            result.add_error(f"Unexpected error during testing: {str(e)}")
            
        finally:
            result.execution_time = time.time() - start_time
            result.calculate_status()
            
        return result
