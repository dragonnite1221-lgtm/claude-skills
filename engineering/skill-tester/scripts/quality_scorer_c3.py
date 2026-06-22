# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from quality_scorer_base import *  # noqa: F403,E402
from quality_scorer_p0 import QualityDimension  # noqa: F401,E501


class QualityScorerMixin3:
    def _score_examples(self, dimension: QualityDimension):
        """Score examples and usage clarity"""
        score = 0
        
        # Look for example files in various locations
        example_locations = ["examples", "assets", "scripts"]
        example_files = []
        
        for location in example_locations:
            location_path = self.skill_path / location
            if location_path.exists():
                example_files.extend(location_path.glob("*example*"))
                example_files.extend(location_path.glob("*sample*"))
                example_files.extend(location_path.glob("*demo*"))
                
        # Score based on example availability
        if len(example_files) >= 3:
            score = 25
        elif len(example_files) >= 2:
            score = 20
        elif len(example_files) >= 1:
            score = 15
        else:
            score = 10
            dimension.add_suggestion("Add more usage examples and sample files")
            
        dimension.add_score("examples_availability", score, 25,
                           f"Found {len(example_files)} example/sample files")
    def _score_code_quality(self, weight: float = 0.25):
        """Score code quality"""
        self.log_verbose("Scoring code quality...")
        
        dimension = QualityDimension("Code Quality", weight, "Quality of Python scripts and implementation")
        
        scripts_dir = self.skill_path / "scripts"
        if not scripts_dir.exists():
            dimension.add_score("scripts_existence", 0, 100, "No scripts directory")
            dimension.add_suggestion("Create scripts directory with Python files")
            dimension.calculate_final_score()
            self.report.add_dimension(dimension)
            return
            
        python_files = list(scripts_dir.glob("*.py"))
        if not python_files:
            dimension.add_score("python_scripts", 0, 100, "No Python scripts found")
            dimension.add_suggestion("Add Python scripts to scripts directory")
            dimension.calculate_final_score()
            self.report.add_dimension(dimension)
            return
            
        # Score script complexity and quality
        self._score_script_complexity(python_files, dimension)
        
        # Score error handling
        self._score_error_handling(python_files, dimension)
        
        # Score code structure
        self._score_code_structure(python_files, dimension)
        
        # Score output format support
        self._score_output_support(python_files, dimension)
        
        dimension.calculate_final_score()
        self.report.add_dimension(dimension)
    def _score_script_complexity(self, python_files: List[Path], dimension: QualityDimension):
        """Score script complexity and sophistication"""
        total_complexity = 0
        script_count = len(python_files)
        
        for script_path in python_files:
            try:
                content = script_path.read_text(encoding='utf-8')
                
                # Count lines of code (excluding empty lines and comments)
                lines = content.split('\n')
                loc = len([line for line in lines if line.strip() and not line.strip().startswith('#')])
                
                # Score based on LOC
                if loc >= 800:
                    complexity_score = 25
                elif loc >= 500:
                    complexity_score = 20
                elif loc >= 300:
                    complexity_score = 15
                elif loc >= 100:
                    complexity_score = 10
                else:
                    complexity_score = 5
                    
                total_complexity += complexity_score
                
            except Exception:
                continue
                
        avg_complexity = total_complexity / script_count if script_count > 0 else 0
        dimension.add_score("script_complexity", avg_complexity, 25,
                           f"Average script complexity across {script_count} scripts")
                           
        if avg_complexity < 15:
            dimension.add_suggestion("Consider expanding scripts with more functionality")
