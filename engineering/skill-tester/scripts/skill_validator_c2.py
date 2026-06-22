# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from skill_validator_base import *  # noqa: F403,E402


class SkillValidatorMixin2:
    def _validate_directory_structure(self):
        """Validate directory structure against tier requirements"""
        self.log_verbose("Validating directory structure...")
        
        # scripts/, references/, assets/ are all optional in the repo's skill
        # contract, so nothing is mandatory unless a specific --tier is targeted.
        required_dirs = self._get_tier_requirement("required_dirs", [])
        optional_dirs = self._get_tier_requirement(
            "optional_dirs", ["scripts", "references", "assets"]
        )
        
        # Check required directories
        missing_required = []
        for dir_name in required_dirs:
            dir_path = self.skill_path / dir_name
            if dir_path.exists() and dir_path.is_dir():
                self.report.add_check(f"dir_{dir_name}_exists", True,
                                     f"{dir_name}/ directory found", 1.0)
            else:
                missing_required.append(dir_name)
                self.report.add_check(f"dir_{dir_name}_exists", False,
                                     f"{dir_name}/ directory missing", 0.0)
                
        if missing_required:
            self.report.add_error(f"Missing required directories: {', '.join(missing_required)}")
            
        # Check optional directories and provide suggestions
        missing_optional = []
        for dir_name in optional_dirs:
            dir_path = self.skill_path / dir_name
            if not (dir_path.exists() and dir_path.is_dir()):
                missing_optional.append(dir_name)
                
        if missing_optional:
            self.report.add_suggestion(f"Consider adding optional directories: {', '.join(missing_optional)}")
    def _validate_python_scripts(self):
        """Validate Python scripts in the scripts directory"""
        self.log_verbose("Validating Python scripts...")
        
        scripts_dir = self.skill_path / "scripts"
        if not scripts_dir.exists():
            return
            
        python_files = list(scripts_dir.glob("*.py"))
        min_scripts = self._get_tier_requirement("min_scripts", 1)
        
        # Check minimum number of scripts
        if len(python_files) >= min_scripts:
            self.report.add_check("min_scripts_count", True,
                                 f"Found {len(python_files)} Python scripts (≥{min_scripts})", 1.0)
        else:
            self.report.add_check("min_scripts_count", False,
                                 f"Found {len(python_files)} Python scripts (<{min_scripts})", 0.0)
            self.report.add_error(f"Insufficient scripts: {len(python_files)}, minimum {min_scripts}")
            
        # Validate each script
        for script_path in python_files:
            self._validate_single_script(script_path)
    def _validate_single_script(self, script_path: Path):
        """Validate a single Python script"""
        script_name = script_path.name
        self.log_verbose(f"Validating script: {script_name}")
        
        try:
            content = script_path.read_text(encoding='utf-8')
            
            # Count lines of code (excluding empty lines and comments)
            lines = content.split('\n')
            loc = len([line for line in lines if line.strip() and not line.strip().startswith('#')])
            
            # Check script size against tier requirements
            size_range = self._get_tier_requirement("script_size_range", (100, 1000))
            min_size, max_size = size_range
            
            if min_size <= loc <= max_size:
                self.report.add_check(f"script_size_{script_name}", True,
                                     f"{script_name} has {loc} LOC (within {min_size}-{max_size})", 1.0)
            else:
                self.report.add_check(f"script_size_{script_name}", False,
                                     f"{script_name} has {loc} LOC (outside {min_size}-{max_size})", 0.5)
                if loc < min_size:
                    self.report.add_suggestion(f"Consider expanding {script_name} (currently {loc} LOC)")
                else:
                    self.report.add_suggestion(f"Consider refactoring {script_name} (currently {loc} LOC)")
                    
            # Parse and validate Python syntax
            try:
                tree = ast.parse(content)
                self.report.add_check(f"script_syntax_{script_name}", True,
                                     f"{script_name} has valid Python syntax", 1.0)
                                     
                # Check for required features
                self._validate_script_features(tree, script_name, content)
                
            except SyntaxError as e:
                self.report.add_check(f"script_syntax_{script_name}", False,
                                     f"{script_name} has syntax error: {str(e)}", 0.0)
                self.report.add_error(f"Syntax error in {script_name}: {str(e)}")
                
        except Exception as e:
            self.report.add_check(f"script_readable_{script_name}", False,
                                 f"Cannot read {script_name}: {str(e)}", 0.0)
            self.report.add_error(f"Cannot read {script_name}: {str(e)}")
