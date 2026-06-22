# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from customer_interview_analyzer_base import *  # noqa: F403,E402


class InterviewAnalyzerMixin0:
    """Analyze customer interviews for insights and patterns"""
    def __init__(self):
        # Pain point indicators
        self.pain_indicators = [
            'frustrat', 'annoy', 'difficult', 'hard', 'confus', 'slow',
            'problem', 'issue', 'struggle', 'challeng', 'pain', 'waste',
            'manual', 'repetitive', 'tedious', 'boring', 'time-consuming',
            'complicated', 'complex', 'unclear', 'wish', 'need', 'want'
        ]
        
        # Positive indicators
        self.delight_indicators = [
            'love', 'great', 'awesome', 'amazing', 'perfect', 'easy',
            'simple', 'quick', 'fast', 'helpful', 'useful', 'valuable',
            'save', 'efficient', 'convenient', 'intuitive', 'clear'
        ]
        
        # Feature request indicators
        self.request_indicators = [
            'would be nice', 'wish', 'hope', 'want', 'need', 'should',
            'could', 'would love', 'if only', 'it would help', 'suggest',
            'recommend', 'idea', 'what if', 'have you considered'
        ]
        
        # Jobs to be done patterns
        self.jtbd_patterns = [
            r'when i\s+(.+?),\s+i want to\s+(.+?)\s+so that\s+(.+)',
            r'i need to\s+(.+?)\s+because\s+(.+)',
            r'my goal is to\s+(.+)',
            r'i\'m trying to\s+(.+)',
            r'i use \w+ to\s+(.+)',
            r'helps me\s+(.+)',
        ]
    def analyze_interview(self, text: str) -> Dict:
        """Analyze a single interview transcript"""
        text_lower = text.lower()
        sentences = self._split_sentences(text)
        
        analysis = {
            'pain_points': self._extract_pain_points(sentences),
            'delights': self._extract_delights(sentences),
            'feature_requests': self._extract_requests(sentences),
            'jobs_to_be_done': self._extract_jtbd(text_lower),
            'sentiment_score': self._calculate_sentiment(text_lower),
            'key_themes': self._extract_themes(text_lower),
            'quotes': self._extract_key_quotes(sentences),
            'metrics_mentioned': self._extract_metrics(text),
            'competitors_mentioned': self._extract_competitors(text)
        }
        
        return analysis
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    def _extract_pain_points(self, sentences: List[str]) -> List[Dict]:
        """Extract pain points from sentences"""
        pain_points = []
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            for indicator in self.pain_indicators:
                if indicator in sentence_lower:
                    # Extract context around the pain point
                    pain_points.append({
                        'quote': sentence,
                        'indicator': indicator,
                        'severity': self._assess_severity(sentence_lower)
                    })
                    break
        
        return pain_points[:10]  # Return top 10
    def _extract_delights(self, sentences: List[str]) -> List[Dict]:
        """Extract positive feedback"""
        delights = []
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            for indicator in self.delight_indicators:
                if indicator in sentence_lower:
                    delights.append({
                        'quote': sentence,
                        'indicator': indicator,
                        'strength': self._assess_strength(sentence_lower)
                    })
                    break
        
        return delights[:10]
    def _extract_requests(self, sentences: List[str]) -> List[Dict]:
        """Extract feature requests and suggestions"""
        requests = []
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            for indicator in self.request_indicators:
                if indicator in sentence_lower:
                    requests.append({
                        'quote': sentence,
                        'type': self._classify_request(sentence_lower),
                        'priority': self._assess_request_priority(sentence_lower)
                    })
                    break
        
        return requests[:10]
