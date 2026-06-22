# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from quality_scorer_base import *  # noqa: F403,E402
from quality_scorer_p0 import QualityDimension  # noqa: F401,E501


class QualityScorerMixin4:
    def _score_error_handling(self, python_files: List[Path], dimension: QualityDimension):
        """Score error handling quality"""
        total_error_score = 0
        script_count = len(python_files)
        
        for script_path in python_files:
            try:
                content = script_path.read_text(encoding='utf-8')
                error_score = 0
                
                # Check for try/except blocks
                try_count = content.count('try:')
                error_score += min(try_count * 5, 15)  # Up to 15 points for try/except
                
                # Check for specific exception handling
                exception_types = ['Exception', 'ValueError', 'FileNotFoundError', 'KeyError', 'TypeError']
                for exc_type in exception_types:
                    if exc_type in content:
                        error_score += 2  # 2 points per specific exception type
                        
                # Check for logging or error reporting
                if any(indicator in content for indicator in ['print(', 'logging.', 'sys.stderr']):
                    error_score += 5  # 5 points for error reporting
                    
                total_error_score += min(error_score, 25)  # Cap at 25 per script
                
            except Exception:
                continue
                
        avg_error_score = total_error_score / script_count if script_count > 0 else 0
        dimension.add_score("error_handling", avg_error_score, 25,
                           f"Error handling quality across {script_count} scripts")
                           
        if avg_error_score < 15:
            dimension.add_suggestion("Improve error handling with try/except blocks and meaningful error messages")
    def _score_code_structure(self, python_files: List[Path], dimension: QualityDimension):
        """Score code structure and organization"""
        total_structure_score = 0
        script_count = len(python_files)
        
        for script_path in python_files:
            try:
                content = script_path.read_text(encoding='utf-8')
                structure_score = 0
                
                # Check for functions and classes
                function_count = content.count('def ')
                class_count = content.count('class ')
                
                structure_score += min(function_count * 2, 10)  # Up to 10 points for functions
                structure_score += min(class_count * 3, 9)     # Up to 9 points for classes
                
                # Check for docstrings
                docstring_patterns = ['"""', "'''", 'def.*:\n.*"""', 'class.*:\n.*"""']
                for pattern in docstring_patterns:
                    if re.search(pattern, content):
                        structure_score += 1  # 1 point per docstring indicator
                        
                # Check for if __name__ == "__main__"
                if 'if __name__ == "__main__"' in content:
                    structure_score += 3
                    
                # Check for imports organization
                if content.lstrip().startswith(('import ', 'from ')):
                    structure_score += 2  # Imports at top
                    
                total_structure_score += min(structure_score, 25)
                
            except Exception:
                continue
                
        avg_structure_score = total_structure_score / script_count if script_count > 0 else 0
        dimension.add_score("code_structure", avg_structure_score, 25,
                           f"Code structure quality across {script_count} scripts")
                           
        if avg_structure_score < 15:
            dimension.add_suggestion("Improve code structure with more functions, classes, and documentation")
    def _score_output_support(self, python_files: List[Path], dimension: QualityDimension):
        """Score output format support"""
        total_output_score = 0
        script_count = len(python_files)
        
        for script_path in python_files:
            try:
                content = script_path.read_text(encoding='utf-8')
                output_score = 0
                
                # Check for JSON support
                if any(indicator in content for indicator in ['json.dump', 'json.load', '--json']):
                    output_score += 12  # JSON support
                    
                # Check for formatted output
                if any(indicator in content for indicator in ['print(f"', 'print("', '.format(', 'f"']):
                    output_score += 8  # Human-readable output
                    
                # Check for argparse help
                if '--help' in content or 'add_help=' in content:
                    output_score += 5  # Help functionality
                    
                total_output_score += min(output_score, 25)
                
            except Exception:
                continue
                
        avg_output_score = total_output_score / script_count if script_count > 0 else 0
        dimension.add_score("output_support", avg_output_score, 25,
                           f"Output format support across {script_count} scripts")
                           
        if avg_output_score < 15:
            dimension.add_suggestion("Add support for both JSON and human-readable output formats")
