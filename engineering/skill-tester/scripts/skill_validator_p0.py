# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from skill_validator_base import *  # noqa: F403,E402


try:
    import yaml
except ImportError:
    # Minimal YAML subset: parse simple key: value frontmatter without pyyaml
    class _YamlStub:
        class YAMLError(Exception):
            pass
        @staticmethod
        def safe_load(text):
            result = {}
            for line in text.strip().splitlines():
                if ':' in line:
                    key, _, value = line.partition(':')
                    result[key.strip()] = value.strip()
            return result if result else None
    yaml = _YamlStub()


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


class ValidationReport:
    """Container for validation results"""
    
    def __init__(self, skill_path: str):
        self.skill_path = skill_path
        self.timestamp = dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")
        self.checks = {}
        self.warnings = []
        self.errors = []
        self.suggestions = []
        self.overall_score = 0.0
        self.compliance_level = "FAIL"
        
    def add_check(self, check_name: str, passed: bool, message: str = "", score: float = 0.0):
        """Add a validation check result"""
        self.checks[check_name] = {
            "passed": passed,
            "message": message,
            "score": score
        }
        
    def add_warning(self, message: str):
        """Add a warning message"""
        self.warnings.append(message)
        
    def add_error(self, message: str):
        """Add an error message"""
        self.errors.append(message)
        
    def add_suggestion(self, message: str):
        """Add an improvement suggestion"""
        self.suggestions.append(message)
        
    def calculate_overall_score(self):
        """Calculate overall compliance score"""
        if not self.checks:
            self.overall_score = 0.0
            return
            
        total_score = sum(check["score"] for check in self.checks.values())
        max_score = len(self.checks) * 1.0
        self.overall_score = (total_score / max_score) * 100 if max_score > 0 else 0.0
        
        # Determine compliance level
        if self.overall_score >= 90:
            self.compliance_level = "EXCELLENT"
        elif self.overall_score >= 75:
            self.compliance_level = "GOOD"
        elif self.overall_score >= 60:
            self.compliance_level = "ACCEPTABLE"
        elif self.overall_score >= 40:
            self.compliance_level = "NEEDS_IMPROVEMENT"
        else:
            self.compliance_level = "POOR"
