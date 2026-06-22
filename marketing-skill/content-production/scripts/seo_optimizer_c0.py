# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from seo_optimizer_base import *  # noqa: F403,E402


class SEOOptimizerMixin0:
    def __init__(self):
        # Common stop words to filter
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
            'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'could', 'should', 'may', 'might', 'must', 'can', 'shall'
        }
        
        # SEO best practices
        self.best_practices = {
            'title_length': (50, 60),
            'meta_description_length': (150, 160),
            'url_length': (50, 60),
            'paragraph_length': (40, 150),
            'heading_keyword_placement': True,
            'keyword_density': (0.01, 0.03)  # 1-3%
        }
    def analyze(self, content: str, target_keyword: str = None, 
                secondary_keywords: List[str] = None) -> Dict:
        """Analyze content for SEO optimization"""
        
        analysis = {
            'content_length': len(content.split()),
            'keyword_analysis': {},
            'structure_analysis': self._analyze_structure(content),
            'readability': self._analyze_readability(content),
            'meta_suggestions': {},
            'optimization_score': 0,
            'recommendations': []
        }
        
        # Keyword analysis
        if target_keyword:
            analysis['keyword_analysis'] = self._analyze_keywords(
                content, target_keyword, secondary_keywords or []
            )
        
        # Generate meta suggestions
        analysis['meta_suggestions'] = self._generate_meta_suggestions(
            content, target_keyword
        )
        
        # Calculate optimization score
        analysis['optimization_score'] = self._calculate_seo_score(analysis)
        
        # Generate recommendations
        analysis['recommendations'] = self._generate_recommendations(analysis)
        
        return analysis
    def _analyze_keywords(self, content: str, primary: str, 
                         secondary: List[str]) -> Dict:
        """Analyze keyword usage and density"""
        content_lower = content.lower()
        word_count = len(content.split())
        
        results = {
            'primary_keyword': {
                'keyword': primary,
                'count': content_lower.count(primary.lower()),
                'density': 0,
                'in_title': False,
                'in_headings': False,
                'in_first_paragraph': False
            },
            'secondary_keywords': [],
            'lsi_keywords': []
        }
        
        # Calculate primary keyword metrics
        if word_count > 0:
            results['primary_keyword']['density'] = (
                results['primary_keyword']['count'] / word_count
            )
        
        # Check keyword placement
        first_para = content.split('\n\n')[0] if '\n\n' in content else content[:200]
        results['primary_keyword']['in_first_paragraph'] = (
            primary.lower() in first_para.lower()
        )
        
        # Analyze secondary keywords
        for keyword in secondary:
            count = content_lower.count(keyword.lower())
            results['secondary_keywords'].append({
                'keyword': keyword,
                'count': count,
                'density': count / word_count if word_count > 0 else 0
            })
        
        # Extract potential LSI keywords
        results['lsi_keywords'] = self._extract_lsi_keywords(content, primary)
        
        return results
