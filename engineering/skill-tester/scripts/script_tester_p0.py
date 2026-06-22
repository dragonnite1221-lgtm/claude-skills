# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from script_tester_base import *  # noqa: F403,E402


class TestError(Exception):
    """Custom exception for testing errors"""
    pass


class ScriptTestResult:
    """Container for individual script test results"""
    
    def __init__(self, script_path: str):
        self.script_path = script_path
        self.script_name = Path(script_path).name
        self.timestamp = datetime.utcnow().isoformat() + "Z"
        self.tests = {}
        self.overall_status = "PENDING"
        self.execution_time = 0.0
        self.errors = []
        self.warnings = []
        
    def add_test(self, test_name: str, passed: bool, message: str = "", details: Dict = None):
        """Add a test result"""
        self.tests[test_name] = {
            "passed": passed,
            "message": message,
            "details": details or {}
        }
        
    def add_error(self, error: str):
        """Add an error message"""
        self.errors.append(error)
        
    def add_warning(self, warning: str):
        """Add a warning message"""
        self.warnings.append(warning)
        
    def calculate_status(self):
        """Calculate overall test status"""
        if not self.tests:
            self.overall_status = "NO_TESTS"
            return
            
        failed_tests = [name for name, result in self.tests.items() if not result["passed"]]
        
        if not failed_tests:
            self.overall_status = "PASS"
        elif len(failed_tests) <= len(self.tests) // 2:
            self.overall_status = "PARTIAL"
        else:
            self.overall_status = "FAIL"


class TestSuite:
    """Container for all test results"""
    
    def __init__(self, skill_path: str):
        self.skill_path = skill_path
        self.timestamp = datetime.utcnow().isoformat() + "Z"
        self.script_results = {}
        self.summary = {}
        self.global_errors = []
        
    def add_script_result(self, result: ScriptTestResult):
        """Add a script test result"""
        self.script_results[result.script_name] = result
        
    def add_global_error(self, error: str):
        """Add a global error message"""
        self.global_errors.append(error)
        
    def calculate_summary(self):
        """Calculate summary statistics"""
        if not self.script_results:
            self.summary = {
                "total_scripts": 0,
                "passed": 0,
                "partial": 0,
                "failed": 0,
                "overall_status": "NO_SCRIPTS"
            }
            return
            
        statuses = [result.overall_status for result in self.script_results.values()]
        
        self.summary = {
            "total_scripts": len(self.script_results),
            "passed": statuses.count("PASS"),
            "partial": statuses.count("PARTIAL"),
            "failed": statuses.count("FAIL"),
            "no_tests": statuses.count("NO_TESTS")
        }
        
        # Determine overall status
        if self.summary["failed"] == 0 and self.summary["no_tests"] == 0:
            self.summary["overall_status"] = "PASS"
        elif self.summary["passed"] > 0:
            self.summary["overall_status"] = "PARTIAL"
        else:
            self.summary["overall_status"] = "FAIL"
