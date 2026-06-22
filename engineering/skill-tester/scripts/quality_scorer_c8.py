# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from quality_scorer_base import *  # noqa: F403,E402
from quality_scorer_p0 import QualityDimension  # noqa: F401,E501


class QualityScorerMixin8:
    def _score_security(self, weight: float = 0.20):
        """Score security quality"""
        self.log_verbose("Scoring security quality...")
        
        dimension = QualityDimension("Security", weight, "Security practices and vulnerability prevention")
        
        # Find Python scripts
        python_files = list(self.skill_path.rglob("*.py"))
        
        # Filter out test files and __pycache__
        python_files = [f for f in python_files 
                       if "__pycache__" not in str(f) and "test_" not in f.name]
        
        if not python_files:
            dimension.add_score("scripts_existence", 25, 25, 
                               "No scripts directory - no script security concerns")
            dimension.calculate_final_score()
            self.report.add_dimension(dimension)
            return
        
        # Use SecurityScorer module
        try:
            scorer = SecurityScorer(python_files, verbose=self.verbose)
            result = scorer.get_overall_score()
            
            # Extract scores from SecurityScorer result
            sensitive_data_score = result.get("sensitive_data_exposure", {}).get("score", 0)
            file_ops_score = result.get("safe_file_operations", {}).get("score", 0)
            command_injection_score = result.get("command_injection_prevention", {}).get("score", 0)
            input_validation_score = result.get("input_validation", {}).get("score", 0)
            
            dimension.add_score("sensitive_data_exposure", sensitive_data_score, 25,
                               "Detection and prevention of hardcoded credentials")
            dimension.add_score("safe_file_operations", file_ops_score, 25,
                               "Prevention of path traversal vulnerabilities")
            dimension.add_score("command_injection_prevention", command_injection_score, 25,
                               "Prevention of command injection vulnerabilities")
            dimension.add_score("input_validation", input_validation_score, 25,
                               "Quality of input validation and error handling")
            
            # Add suggestions from SecurityScorer
            for issue in result.get("issues", []):
                dimension.add_suggestion(issue)
                
        except Exception as e:
            self.log_verbose(f"Security scoring failed: {str(e)}")
            dimension.add_score("security_error", 0, 100, f"Security scoring failed: {str(e)}")
            dimension.add_suggestion("Fix security scoring module integration")
        
        dimension.calculate_final_score()
        self.report.add_dimension(dimension)
