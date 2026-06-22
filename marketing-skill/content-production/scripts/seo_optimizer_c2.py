# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from seo_optimizer_base import *  # noqa: F403,E402


class SEOOptimizerMixin2:
    def _generate_meta_suggestions(self, content: str, keyword: str = None) -> Dict:
        """Generate SEO meta tag suggestions"""
        # Extract first sentence for description base
        sentences = re.split(r'[.!?]+', content)
        first_sentence = sentences[0] if sentences else content[:160]
        
        suggestions = {
            'title': '',
            'meta_description': '',
            'url_slug': '',
            'og_title': '',
            'og_description': ''
        }
        
        if keyword:
            # Title suggestion
            suggestions['title'] = f"{keyword.title()} - Complete Guide"
            if len(suggestions['title']) > 60:
                suggestions['title'] = keyword.title()[:57] + "..."
            
            # Meta description
            desc_base = f"Learn everything about {keyword}. {first_sentence}"
            if len(desc_base) > 160:
                desc_base = desc_base[:157] + "..."
            suggestions['meta_description'] = desc_base
            
            # URL slug
            suggestions['url_slug'] = re.sub(r'[^a-z0-9-]+', '-', 
                                            keyword.lower()).strip('-')
            
            # Open Graph tags
            suggestions['og_title'] = suggestions['title']
            suggestions['og_description'] = suggestions['meta_description']
        
        return suggestions
    def _calculate_seo_score(self, analysis: Dict) -> int:
        """Calculate overall SEO optimization score"""
        score = 0
        max_score = 100
        
        # Content length scoring (20 points)
        if 300 <= analysis['content_length'] <= 2500:
            score += 20
        elif 200 <= analysis['content_length'] < 300:
            score += 10
        elif analysis['content_length'] > 2500:
            score += 15
        
        # Keyword optimization (30 points)
        if analysis['keyword_analysis']:
            kw_data = analysis['keyword_analysis']['primary_keyword']
            
            # Density scoring
            if 0.01 <= kw_data['density'] <= 0.03:
                score += 15
            elif 0.005 <= kw_data['density'] < 0.01:
                score += 8
            
            # Placement scoring
            if kw_data['in_first_paragraph']:
                score += 10
            if kw_data.get('in_headings'):
                score += 5
        
        # Structure scoring (25 points)
        struct = analysis['structure_analysis']
        if struct['headings']['total'] > 0:
            score += 10
        if struct['paragraphs'] >= 3:
            score += 10
        if struct['links']['internal'] > 0 or struct['links']['external'] > 0:
            score += 5
        
        # Readability scoring (25 points)
        readability_score = analysis['readability']['score']
        score += int(readability_score * 0.25)
        
        return min(score, max_score)
