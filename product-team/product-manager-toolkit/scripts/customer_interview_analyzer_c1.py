# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from customer_interview_analyzer_base import *  # noqa: F403,E402


class InterviewAnalyzerMixin1:
    def _extract_jtbd(self, text: str) -> List[Dict]:
        """Extract Jobs to Be Done patterns"""
        jobs = []
        
        for pattern in self.jtbd_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    job = ' → '.join(match)
                else:
                    job = match
                
                jobs.append({
                    'job': job,
                    'pattern': pattern.pattern if hasattr(pattern, 'pattern') else pattern
                })
        
        return jobs[:5]
    def _calculate_sentiment(self, text: str) -> Dict:
        """Calculate overall sentiment of the interview"""
        positive_count = sum(1 for ind in self.delight_indicators if ind in text)
        negative_count = sum(1 for ind in self.pain_indicators if ind in text)
        
        total = positive_count + negative_count
        if total == 0:
            sentiment_score = 0
        else:
            sentiment_score = (positive_count - negative_count) / total
        
        if sentiment_score > 0.3:
            sentiment_label = 'positive'
        elif sentiment_score < -0.3:
            sentiment_label = 'negative'
        else:
            sentiment_label = 'neutral'
        
        return {
            'score': round(sentiment_score, 2),
            'label': sentiment_label,
            'positive_signals': positive_count,
            'negative_signals': negative_count
        }
    def _extract_themes(self, text: str) -> List[str]:
        """Extract key themes using word frequency"""
        # Remove common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at',
                     'to', 'for', 'of', 'with', 'by', 'from', 'as', 'is',
                     'was', 'are', 'were', 'been', 'be', 'have', 'has',
                     'had', 'do', 'does', 'did', 'will', 'would', 'could',
                     'should', 'may', 'might', 'must', 'can', 'shall',
                     'it', 'i', 'you', 'we', 'they', 'them', 'their'}
        
        # Extract meaningful words
        words = re.findall(r'\b[a-z]{4,}\b', text)
        meaningful_words = [w for w in words if w not in stop_words]
        
        # Count frequency
        word_freq = Counter(meaningful_words)
        
        # Extract themes (top frequent meaningful words)
        themes = [word for word, count in word_freq.most_common(10) if count >= 3]
        
        return themes
    def _extract_key_quotes(self, sentences: List[str]) -> List[str]:
        """Extract the most insightful quotes"""
        scored_sentences = []
        
        for sentence in sentences:
            if len(sentence) < 20 or len(sentence) > 200:
                continue
            
            score = 0
            sentence_lower = sentence.lower()
            
            # Score based on insight indicators
            if any(ind in sentence_lower for ind in self.pain_indicators):
                score += 2
            if any(ind in sentence_lower for ind in self.request_indicators):
                score += 2
            if 'because' in sentence_lower:
                score += 1
            if 'but' in sentence_lower:
                score += 1
            if '?' in sentence:
                score += 1
            
            if score > 0:
                scored_sentences.append((score, sentence))
        
        # Sort by score and return top quotes
        scored_sentences.sort(reverse=True)
        return [s[1] for s in scored_sentences[:5]]
