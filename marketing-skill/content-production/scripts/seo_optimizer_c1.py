# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from seo_optimizer_base import *  # noqa: F403,E402


class SEOOptimizerMixin1:
    def _analyze_structure(self, content: str) -> Dict:
        """Analyze content structure for SEO"""
        lines = content.split('\n')
        
        structure = {
            'headings': {'h1': 0, 'h2': 0, 'h3': 0, 'total': 0},
            'paragraphs': 0,
            'lists': 0,
            'images': 0,
            'links': {'internal': 0, 'external': 0},
            'avg_paragraph_length': 0
        }
        
        paragraphs = []
        current_para = []
        
        for line in lines:
            # Count headings
            if line.startswith('# '):
                structure['headings']['h1'] += 1
                structure['headings']['total'] += 1
            elif line.startswith('## '):
                structure['headings']['h2'] += 1
                structure['headings']['total'] += 1
            elif line.startswith('### '):
                structure['headings']['h3'] += 1
                structure['headings']['total'] += 1
            
            # Count lists
            if line.strip().startswith(('- ', '* ', '1. ')):
                structure['lists'] += 1
            
            # Count links
            internal_links = len(re.findall(r'\[.*?\]\(/.*?\)', line))
            external_links = len(re.findall(r'\[.*?\]\(https?://.*?\)', line))
            structure['links']['internal'] += internal_links
            structure['links']['external'] += external_links
            
            # Track paragraphs
            if line.strip() and not line.startswith('#'):
                current_para.append(line)
            elif current_para:
                paragraphs.append(' '.join(current_para))
                current_para = []
        
        if current_para:
            paragraphs.append(' '.join(current_para))
        
        structure['paragraphs'] = len(paragraphs)
        
        if paragraphs:
            avg_length = sum(len(p.split()) for p in paragraphs) / len(paragraphs)
            structure['avg_paragraph_length'] = round(avg_length, 1)
        
        return structure
    def _analyze_readability(self, content: str) -> Dict:
        """Analyze content readability"""
        sentences = re.split(r'[.!?]+', content)
        words = content.split()
        
        if not sentences or not words:
            return {'score': 0, 'level': 'Unknown'}
        
        avg_sentence_length = len(words) / len(sentences)
        
        # Simple readability scoring
        if avg_sentence_length < 15:
            level = 'Easy'
            score = 90
        elif avg_sentence_length < 20:
            level = 'Moderate'
            score = 70
        elif avg_sentence_length < 25:
            level = 'Difficult'
            score = 50
        else:
            level = 'Very Difficult'
            score = 30
        
        return {
            'score': score,
            'level': level,
            'avg_sentence_length': round(avg_sentence_length, 1)
        }
    def _extract_lsi_keywords(self, content: str, primary_keyword: str) -> List[str]:
        """Extract potential LSI (semantically related) keywords"""
        words = re.findall(r'\b[a-z]+\b', content.lower())
        word_freq = {}
        
        # Count word frequencies
        for word in words:
            if word not in self.stop_words and len(word) > 3:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and return top related terms
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        # Filter out the primary keyword and return top 10
        lsi_keywords = []
        for word, count in sorted_words:
            if word != primary_keyword.lower() and count > 1:
                lsi_keywords.append(word)
            if len(lsi_keywords) >= 10:
                break
        
        return lsi_keywords
