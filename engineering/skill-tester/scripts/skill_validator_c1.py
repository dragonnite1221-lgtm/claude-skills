# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from skill_validator_base import *  # noqa: F403,E402


class SkillValidatorMixin1:
    def _validate_frontmatter(self, content: str):
        """Validate SKILL.md frontmatter"""
        self.log_verbose("Validating frontmatter...")
        
        # Extract frontmatter
        if content.startswith('---'):
            try:
                end_marker = content.find('---', 3)
                if end_marker == -1:
                    self.report.add_check("frontmatter_format", False, 
                                         "Frontmatter closing marker not found", 0.0)
                    return
                    
                frontmatter_text = content[3:end_marker].strip()
                frontmatter = yaml.safe_load(frontmatter_text)
                
                if not isinstance(frontmatter, dict):
                    self.report.add_check("frontmatter_format", False, 
                                         "Frontmatter is not a valid dictionary", 0.0)
                    return
                    
                # Check required fields are present AND non-blank. The enforced
                # gate (scripts/validate-skill-frontmatter.py) rejects empty
                # required keys, so presence alone would let a `name: ""` skill
                # pass locally yet fail CI — exactly the local≠CI divergence
                # this alignment is meant to remove.
                missing_fields = []
                for field in self.FRONTMATTER_REQUIRED_FIELDS:
                    value = frontmatter.get(field)
                    if field not in frontmatter or value is None or not str(value).strip():
                        missing_fields.append(field)

                if not missing_fields:
                    self.report.add_check("frontmatter_complete", True,
                                         "All required frontmatter fields present", 1.0)
                else:
                    self.report.add_check("frontmatter_complete", False,
                                         f"Missing fields: {', '.join(missing_fields)}", 0.0)
                    self.report.add_error(f"Missing frontmatter fields: {', '.join(missing_fields)}")
                    
            except yaml.YAMLError as e:
                self.report.add_check("frontmatter_format", False, 
                                     f"Invalid YAML frontmatter: {str(e)}", 0.0)
                self.report.add_error(f"Invalid YAML frontmatter: {str(e)}")
                
        else:
            self.report.add_check("frontmatter_exists", False, 
                                 "No frontmatter found", 0.0)
            self.report.add_error("SKILL.md must start with YAML frontmatter")
    def _validate_required_sections(self, content: str):
        """Validate required sections in SKILL.md"""
        self.log_verbose("Checking required sections...")
        
        # When a custom section list is configured, enforce it. Otherwise the
        # only universal structural requirement is a top-level title (name and
        # description already live in frontmatter).
        if self.REQUIRED_SKILL_MD_SECTIONS:
            missing_sections = []
            for section in self.REQUIRED_SKILL_MD_SECTIONS:
                pattern = rf'^#+\s*{re.escape(section)}\s*$'
                if not re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
                    missing_sections.append(section)

            if not missing_sections:
                self.report.add_check("required_sections", True,
                                     "All required sections present", 1.0)
            else:
                self.report.add_check("required_sections", False,
                                     f"Missing sections: {', '.join(missing_sections)}", 0.0)
                self.report.add_error(f"Missing required sections: {', '.join(missing_sections)}")
            return

        if re.search(r'^#\s+\S', content, re.MULTILINE):
            self.report.add_check("skill_md_title", True, "Top-level title present", 1.0)
        else:
            self.report.add_check("skill_md_title", False, "No top-level (#) title found", 0.0)
            self.report.add_error("SKILL.md must have a top-level '# Title' heading")
    def _validate_readme(self):
        """Validate README.md content"""
        self.log_verbose("Validating README.md...")
        
        readme_path = self.skill_path / "README.md"
        if not readme_path.exists():
            return
            
        try:
            content = readme_path.read_text(encoding='utf-8')
            
            # Check minimum content length
            if len(content.strip()) >= 200:
                self.report.add_check("readme_substantial", True,
                                     "README.md has substantial content", 1.0)
            else:
                self.report.add_check("readme_substantial", False,
                                     "README.md content is too brief", 0.5)
                self.report.add_suggestion("Expand README.md with more detailed usage instructions")
                
        except Exception as e:
            self.report.add_check("readme_readable", False,
                                 f"Error reading README.md: {str(e)}", 0.0)
