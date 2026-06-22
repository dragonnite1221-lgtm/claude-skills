# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from seo_optimizer_base import *  # noqa: F403,E402


class SEOOptimizerMixin3:
    def _generate_recommendations(self, analysis: Dict) -> List[str]:
        """Generate SEO improvement recommendations"""
        recommendations = []
        
        # Content length recommendations
        if analysis['content_length'] < 300:
            recommendations.append(
                f"Increase content length to at least 300 words (currently {analysis['content_length']})"
            )
        elif analysis['content_length'] > 3000:
            recommendations.append(
                "Consider breaking long content into multiple pages or adding a table of contents"
            )
        
        # Keyword recommendations
        if analysis['keyword_analysis']:
            kw_data = analysis['keyword_analysis']['primary_keyword']
            
            if kw_data['density'] < 0.01:
                recommendations.append(
                    f"Increase keyword density for '{kw_data['keyword']}' (currently {kw_data['density']:.2%})"
                )
            elif kw_data['density'] > 0.03:
                recommendations.append(
                    f"Reduce keyword density to avoid over-optimization (currently {kw_data['density']:.2%})"
                )
            
            if not kw_data['in_first_paragraph']:
                recommendations.append(
                    "Include primary keyword in the first paragraph"
                )
        
        # Structure recommendations
        struct = analysis['structure_analysis']
        if struct['headings']['total'] == 0:
            recommendations.append("Add headings (H1, H2, H3) to improve content structure")
        if struct['links']['internal'] == 0:
            recommendations.append("Add internal links to related content")
        if struct['avg_paragraph_length'] > 150:
            recommendations.append("Break up long paragraphs for better readability")
        
        # Readability recommendations
        if analysis['readability']['avg_sentence_length'] > 20:
            recommendations.append("Simplify sentences for better readability")
        
        return recommendations
