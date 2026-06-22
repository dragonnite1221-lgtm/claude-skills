# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from skill_validator_base import *  # noqa: F403,E402
from skill_validator_p0 import ValidationReport  # noqa: F401,E501


class SkillValidatorMixin0:
    """Main skill validation engine"""
    TIER_REQUIREMENTS = {
        "BASIC": {
            "min_skill_md_lines": 100,
            "min_scripts": 1,
            "script_size_range": (100, 300),
            "required_dirs": ["scripts"],
            "optional_dirs": ["assets", "references", "expected_outputs"],
            "features_required": ["argparse", "main_guard"]
        },
        "STANDARD": {
            "min_skill_md_lines": 200,
            "min_scripts": 1,
            "script_size_range": (300, 500),
            "required_dirs": ["scripts", "assets", "references"],
            "optional_dirs": ["expected_outputs"],
            "features_required": ["argparse", "main_guard", "json_output", "help_text"]
        },
        "POWERFUL": {
            "min_skill_md_lines": 300,
            "min_scripts": 2,
            "script_size_range": (500, 800),
            "required_dirs": ["scripts", "assets", "references", "expected_outputs"],
            "optional_dirs": [],
            "features_required": ["argparse", "main_guard", "json_output", "help_text", "error_handling"]
        }
    }
    REQUIRED_SKILL_MD_SECTIONS: list = []
    FRONTMATTER_REQUIRED_FIELDS = ["name", "description"]
    def __init__(self, skill_path: str, target_tier: Optional[str] = None, verbose: bool = False):
        self.skill_path = Path(skill_path).resolve()
        self.target_tier = target_tier
        self.verbose = verbose
        self.report = ValidationReport(str(self.skill_path))
    def log_verbose(self, message: str):
        """Log verbose message if verbose mode enabled"""
        if self.verbose:
            print(f"[VERBOSE] {message}", file=sys.stderr)
    def validate_skill_structure(self) -> ValidationReport:
        """Main validation entry point"""
        try:
            self.log_verbose(f"Starting validation of {self.skill_path}")
            
            # Check if path exists
            if not self.skill_path.exists():
                self.report.add_error(f"Skill path does not exist: {self.skill_path}")
                return self.report
                
            if not self.skill_path.is_dir():
                self.report.add_error(f"Skill path is not a directory: {self.skill_path}")
                return self.report
                
            # Run all validation checks
            self._validate_required_files()
            self._validate_skill_md()
            self._validate_readme()
            self._validate_directory_structure()
            self._validate_python_scripts()
            self._validate_tier_compliance()
            
            # Calculate overall score
            self.report.calculate_overall_score()
            
            self.log_verbose(f"Validation completed. Score: {self.report.overall_score:.1f}")
            
        except Exception as e:
            self.report.add_error(f"Validation failed with exception: {str(e)}")
            
        return self.report
    def _validate_required_files(self):
        """Validate presence of required files"""
        self.log_verbose("Checking required files...")
        
        # Check SKILL.md
        skill_md_path = self.skill_path / "SKILL.md"
        if skill_md_path.exists():
            self.report.add_check("skill_md_exists", True, "SKILL.md found", 1.0)
        else:
            self.report.add_check("skill_md_exists", False, "SKILL.md missing", 0.0)
            self.report.add_error("SKILL.md is required but missing")
            
        # Check README.md
        # README.md is not part of the skill contract (CLAUDE.md skill package
        # = SKILL.md + optional scripts/references/assets). Treat it as advisory
        # so its absence does not lower the contract-compliance score.
        readme_path = self.skill_path / "README.md"
        if readme_path.exists():
            self.report.add_check("readme_present", True, "README.md present (optional)", 1.0)
        else:
            self.report.add_check("readme_present", True,
                                 "README.md optional — not part of skill contract", 1.0)
            self.report.add_suggestion("Optional: add README.md for standalone usage docs")
    def _validate_skill_md(self):
        """Validate SKILL.md content and format"""
        self.log_verbose("Validating SKILL.md...")
        
        skill_md_path = self.skill_path / "SKILL.md"
        if not skill_md_path.exists():
            return
            
        try:
            content = skill_md_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            line_count = len([line for line in lines if line.strip()])
            
            # Check line count. With no --tier, only flag genuine stubs: Tessl
            # skill review rewards concision (a 78-line skill can score 100/100),
            # so a 100-line floor would push skills toward bloat the real quality
            # gate penalizes. Tier-specific minimums still apply when targeted.
            min_lines = self._get_tier_requirement("min_skill_md_lines", 20)
            if line_count >= min_lines:
                self.report.add_check("skill_md_length", True, 
                                     f"SKILL.md has {line_count} lines (≥{min_lines})", 1.0)
            else:
                self.report.add_check("skill_md_length", False,
                                     f"SKILL.md has {line_count} lines (<{min_lines})", 0.0)
                self.report.add_error(f"SKILL.md too short: {line_count} lines, minimum {min_lines}")
                
            # Validate frontmatter
            self._validate_frontmatter(content)
            
            # Check required sections
            self._validate_required_sections(content)
            
        except Exception as e:
            self.report.add_check("skill_md_readable", False, f"Error reading SKILL.md: {str(e)}", 0.0)
            self.report.add_error(f"Cannot read SKILL.md: {str(e)}")
