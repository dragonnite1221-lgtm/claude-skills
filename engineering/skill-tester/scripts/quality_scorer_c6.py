# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from quality_scorer_base import *  # noqa: F403,E402
from quality_scorer_p0 import QualityDimension  # noqa: F401,E501


class QualityScorerMixin6:
    def _score_test_coverage(self, dimension: QualityDimension):
        """Score test coverage and validation"""
        # This is a simplified scoring - in a more sophisticated system,
        # this would integrate with actual test runners
        
        score = 15  # Base score for having a structure
        
        # Check for test-related files
        test_indicators = ["test", "spec", "check"]
        test_files = []
        
        for indicator in test_indicators:
            test_files.extend(self.skill_path.rglob(f"*{indicator}*"))
            
        if test_files:
            score += 10  # Bonus for test files
            
        dimension.add_score("test_coverage", score, 25,
                           f"Test coverage indicators: {len(test_files)} files")
                           
        if not test_files:
            dimension.add_suggestion("Add test files or validation scripts")
    def _score_usability(self, weight: float = 0.25):
        """Score usability"""
        self.log_verbose("Scoring usability...")
        
        dimension = QualityDimension("Usability", weight, "Ease of use and user experience")
        
        # Score installation simplicity
        self._score_installation(dimension)
        
        # Score usage clarity
        self._score_usage_clarity(dimension)
        
        # Score help and documentation accessibility
        self._score_help_accessibility(dimension)
        
        # Score practical examples
        self._score_practical_examples(dimension)
        
        dimension.calculate_final_score()
        self.report.add_dimension(dimension)
    def _score_installation(self, dimension: QualityDimension):
        """Score installation simplicity"""
        # Check for installation complexity indicators
        score = 25  # Start with full points for standard library only approach
        
        # Check for requirements.txt or setup.py (would reduce score)
        if (self.skill_path / "requirements.txt").exists():
            score -= 5  # Minor penalty for external dependencies
            dimension.add_suggestion("Consider removing external dependencies for easier installation")
            
        if (self.skill_path / "setup.py").exists():
            score -= 3  # Minor penalty for complex setup
            
        dimension.add_score("installation_simplicity", max(score, 15), 25,
                           "Installation complexity assessment")
    def _score_usage_clarity(self, dimension: QualityDimension):
        """Score usage clarity"""
        score = 0
        
        # Check README for usage instructions
        readme_path = self.skill_path / "README.md"
        if readme_path.exists():
            try:
                content = readme_path.read_text(encoding='utf-8').lower()
                if 'usage' in content or 'how to' in content:
                    score += 10
                if 'example' in content:
                    score += 5
            except:
                pass
                
        # Check scripts for help text quality
        scripts_dir = self.skill_path / "scripts"
        if scripts_dir.exists():
            python_files = list(scripts_dir.glob("*.py"))
            help_quality = 0
            
            for script_path in python_files:
                try:
                    content = script_path.read_text(encoding='utf-8')
                    if 'argparse' in content and 'help=' in content:
                        help_quality += 2
                except:
                    continue
                    
            score += min(help_quality, 10)  # Up to 10 points for help text
            
        dimension.add_score("usage_clarity", score, 25, "Usage instructions and help quality")
        
        if score < 15:
            dimension.add_suggestion("Improve usage documentation and help text")
