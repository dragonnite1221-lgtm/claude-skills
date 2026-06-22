# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from quality_scorer_base import *  # noqa: F403,E402
from quality_scorer_p0 import QualityDimension  # noqa: F401,E501


class QualityScorerMixin7:
    def _score_help_accessibility(self, dimension: QualityDimension):
        """Score help and documentation accessibility"""
        score = 0
        
        # Check for comprehensive help in scripts
        scripts_dir = self.skill_path / "scripts"
        if scripts_dir.exists():
            python_files = list(scripts_dir.glob("*.py"))
            
            for script_path in python_files:
                try:
                    content = script_path.read_text(encoding='utf-8')
                    
                    # Check for detailed help text
                    if 'epilog=' in content or 'description=' in content:
                        score += 5  # Detailed help
                        
                    # Check for examples in help
                    if 'examples:' in content.lower() or 'example:' in content.lower():
                        score += 3  # Examples in help
                        
                except:
                    continue
                    
        # Check for documentation files
        doc_files = list(self.skill_path.glob("*.md"))
        if len(doc_files) >= 2:
            score += 5  # Multiple documentation files
            
        dimension.add_score("help_accessibility", min(score, 25), 25,
                           "Help and documentation accessibility")
                           
        if score < 15:
            dimension.add_suggestion("Add more comprehensive help text and documentation")
    def _score_practical_examples(self, dimension: QualityDimension):
        """Score practical examples quality"""
        score = 0
        
        # Look for example files
        example_patterns = ["*example*", "*sample*", "*demo*", "*tutorial*"]
        example_files = []
        
        for pattern in example_patterns:
            example_files.extend(self.skill_path.rglob(pattern))
            
        # Score based on example availability and quality
        if len(example_files) >= 5:
            score = 25
        elif len(example_files) >= 3:
            score = 20
        elif len(example_files) >= 2:
            score = 15
        elif len(example_files) >= 1:
            score = 10
        else:
            score = 5
            dimension.add_suggestion("Add more practical examples and sample files")
            
        dimension.add_score("practical_examples", score, 25,
                           f"Practical examples: {len(example_files)} files")
