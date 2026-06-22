# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from quality_scorer_base import *  # noqa: F403,E402
from quality_scorer_p0 import QualityDimension  # noqa: F401,E501


class QualityScorerMixin2:
    def _score_sections(self, content: str) -> float:
        """Score section completeness"""
        required_sections = ["Description", "Features", "Usage", "Examples"]
        recommended_sections = ["Architecture", "Installation", "Troubleshooting", "Contributing"]
        
        score = 0
        
        # Required sections (15 points)
        present_required = 0
        for section in required_sections:
            if re.search(rf'^#+\s*{re.escape(section)}\s*$', content, re.MULTILINE | re.IGNORECASE):
                present_required += 1
                
        score += (present_required / len(required_sections)) * 15
        
        # Recommended sections (10 points)
        present_recommended = 0
        for section in recommended_sections:
            if re.search(rf'^#+\s*{re.escape(section)}\s*$', content, re.MULTILINE | re.IGNORECASE):
                present_recommended += 1
                
        score += (present_recommended / len(recommended_sections)) * 10
        
        return score
    def _score_content_depth(self, content: str) -> float:
        """Score content depth and technical detail"""
        score = 0
        
        # Code examples (8 points)
        code_blocks = len(re.findall(r'```[\w]*\n.*?\n```', content, re.DOTALL))
        score += min(code_blocks * 2, 8)
        
        # Technical depth indicators (8 points)
        depth_indicators = ['API', 'algorithm', 'architecture', 'implementation', 'performance', 
                           'scalability', 'security', 'integration', 'configuration', 'parameters']
        depth_score = sum(1 for indicator in depth_indicators if indicator.lower() in content.lower())
        score += min(depth_score * 0.8, 8)
        
        # Usage examples (9 points)
        example_patterns = [r'Example:', r'Usage:', r'```bash', r'```python', r'```yaml']
        example_count = sum(len(re.findall(pattern, content, re.IGNORECASE)) for pattern in example_patterns)
        score += min(example_count * 1.5, 9)
        
        return score
    def _score_readme(self, dimension: QualityDimension):
        """Score README.md quality"""
        readme_path = self.skill_path / "README.md"
        
        if not readme_path.exists():
            dimension.add_score("readme_existence", 10, 25, "README.md exists (partial credit)")
            dimension.add_suggestion("Create README.md with usage instructions")
            return
            
        try:
            content = readme_path.read_text(encoding='utf-8')
            
            # Length and substance
            if len(content.strip()) >= 1000:
                length_score = 25
            elif len(content.strip()) >= 500:
                length_score = 20
            elif len(content.strip()) >= 200:
                length_score = 15
            else:
                length_score = 10
                
            dimension.add_score("readme_quality", length_score, 25,
                               f"README.md content quality ({len(content)} characters)")
                               
            if len(content.strip()) < 500:
                dimension.add_suggestion("Expand README.md with more detailed usage examples")
                
        except Exception:
            dimension.add_score("readme_readable", 5, 25, "README.md exists but has issues")
    def _score_references(self, dimension: QualityDimension):
        """Score reference documentation quality"""
        references_dir = self.skill_path / "references"
        
        if not references_dir.exists():
            dimension.add_score("references_existence", 0, 25, "No references directory")
            dimension.add_suggestion("Add references directory with documentation")
            return
            
        ref_files = list(references_dir.glob("*.md")) + list(references_dir.glob("*.txt"))
        
        if not ref_files:
            dimension.add_score("references_content", 5, 25, "References directory empty")
            dimension.add_suggestion("Add reference documentation files")
            return
            
        # Score based on number and quality of reference files
        score = min(len(ref_files) * 5, 20)  # Up to 20 points for multiple files
        
        # Bonus for substantial content
        total_content = 0
        for ref_file in ref_files:
            try:
                content = ref_file.read_text(encoding='utf-8')
                total_content += len(content.strip())
            except:
                continue
                
        if total_content >= 2000:
            score += 5  # Bonus for substantial reference content
            
        dimension.add_score("references_quality", score, 25, 
                           f"References: {len(ref_files)} files, {total_content} chars")
