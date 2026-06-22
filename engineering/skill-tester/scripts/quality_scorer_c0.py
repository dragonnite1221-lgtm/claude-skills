# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from quality_scorer_base import *  # noqa: F403,E402
from quality_scorer_p0 import QualityDimension  # noqa: F401,E501
from quality_scorer_p1 import QualityReport  # noqa: F401,E501


class QualityScorerMixin0:
    """Main quality scoring engine"""
    def __init__(self, skill_path: str, detailed: bool = False, verbose: bool = False, include_security: bool = False):
        self.skill_path = Path(skill_path).resolve()
        self.detailed = detailed
        self.verbose = verbose
        self.include_security = include_security
        self.report = QualityReport(str(self.skill_path))
    def log_verbose(self, message: str):
        """Log verbose message if verbose mode enabled"""
        if self.verbose:
            print(f"[VERBOSE] {message}", file=sys.stderr)
    def assess_quality(self) -> QualityReport:
        """Main quality assessment entry point"""
        try:
            self.log_verbose(f"Starting quality assessment for {self.skill_path}")
            
            # Check if skill path exists
            if not self.skill_path.exists():
                raise ValueError(f"Skill path does not exist: {self.skill_path}")
                
            # Score each dimension
            # Default: 4 dimensions at 25% each (backward compatible)
            # With --include-security: 5 dimensions at 20% each
            weight = 0.20 if self.include_security else 0.25
            
            self._score_documentation(weight)
            self._score_code_quality(weight)
            self._score_completeness(weight)
            
            if self.include_security:
                self._score_security(0.20)
                self._score_usability(0.20)
            else:
                self._score_usability(0.25)
            
            # Calculate overall metrics
            self.report.calculate_overall_score()
            
            self.log_verbose(f"Quality assessment completed. Overall score: {self.report.overall_score:.1f}")
            
        except Exception as e:
            print(f"Quality assessment failed: {str(e)}", file=sys.stderr)
            raise
            
        return self.report
    def _score_documentation(self, weight: float = 0.25):
        """Score documentation quality"""
        self.log_verbose("Scoring documentation quality...")
        
        dimension = QualityDimension("Documentation", weight, "Quality of documentation and written materials")
        
        # Score SKILL.md
        self._score_skill_md(dimension)
        
        # Score README.md
        self._score_readme(dimension)
        
        # Score reference documentation
        self._score_references(dimension)
        
        # Score examples and usage clarity
        self._score_examples(dimension)
        
        dimension.calculate_final_score()
        self.report.add_dimension(dimension)
