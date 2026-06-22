# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from quality_scorer_base import *  # noqa: F403,E402
from quality_scorer_p0 import QualityDimension  # noqa: F401,E501


class QualityScorerMixin1:
    def _score_skill_md(self, dimension: QualityDimension):
        """Score SKILL.md quality"""
        skill_md_path = self.skill_path / "SKILL.md"
        
        if not skill_md_path.exists():
            dimension.add_score("skill_md_existence", 0, 25, "SKILL.md does not exist")
            dimension.add_suggestion("Create comprehensive SKILL.md file")
            return
            
        try:
            content = skill_md_path.read_text(encoding='utf-8')
            lines = [line for line in content.split('\n') if line.strip()]
            
            # Score based on length and depth
            line_count = len(lines)
            if line_count >= 400:
                length_score = 25
            elif line_count >= 300:
                length_score = 20
            elif line_count >= 200:
                length_score = 15
            elif line_count >= 100:
                length_score = 10
            else:
                length_score = 5
                
            dimension.add_score("skill_md_length", length_score, 25, 
                               f"SKILL.md has {line_count} lines")
                               
            if line_count < 300:
                dimension.add_suggestion("Expand SKILL.md with more detailed sections")
                
            # Score frontmatter quality
            frontmatter_score = self._score_frontmatter(content)
            dimension.add_score("skill_md_frontmatter", frontmatter_score, 25, 
                               "Frontmatter completeness and accuracy")
                               
            # Score section completeness
            section_score = self._score_sections(content)
            dimension.add_score("skill_md_sections", section_score, 25,
                               "Required and recommended section coverage")
                               
            # Score content depth
            depth_score = self._score_content_depth(content)
            dimension.add_score("skill_md_depth", depth_score, 25,
                               "Content depth and technical detail")
                               
        except Exception as e:
            dimension.add_score("skill_md_readable", 0, 25, f"Error reading SKILL.md: {str(e)}")
            dimension.add_suggestion("Fix SKILL.md file encoding or format issues")
    def _score_frontmatter(self, content: str) -> float:
        """Score SKILL.md frontmatter quality"""
        required_fields = ["Name", "Tier", "Category", "Dependencies", "Author", "Version"]
        recommended_fields = ["Last Updated", "Description"]
        
        try:
            if not content.startswith('---'):
                return 5  # Partial credit for having some structure
                
            end_marker = content.find('---', 3)
            if end_marker == -1:
                return 5
                
            frontmatter_text = content[3:end_marker].strip()
            frontmatter = yaml.safe_load(frontmatter_text)
            
            if not isinstance(frontmatter, dict):
                return 5
                
            score = 0
            
            # Required fields (15 points)
            present_required = sum(1 for field in required_fields if field in frontmatter)
            score += (present_required / len(required_fields)) * 15
            
            # Recommended fields (5 points)
            present_recommended = sum(1 for field in recommended_fields if field in frontmatter)
            score += (present_recommended / len(recommended_fields)) * 5
            
            # Quality of field values (5 points)
            quality_bonus = 0
            for field, value in frontmatter.items():
                if isinstance(value, str) and len(value.strip()) > 3:
                    quality_bonus += 0.5
                    
            score += min(quality_bonus, 5)
            
            return min(score, 25)
            
        except yaml.YAMLError:
            return 5  # Some credit for attempting frontmatter
