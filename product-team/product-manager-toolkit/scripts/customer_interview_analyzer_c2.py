# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from customer_interview_analyzer_base import *  # noqa: F403,E402


class InterviewAnalyzerMixin2:
    def _extract_metrics(self, text: str) -> List[str]:
        """Extract any metrics or numbers mentioned"""
        metrics = []
        
        # Find percentages
        percentages = re.findall(r'\d+%', text)
        metrics.extend(percentages)
        
        # Find time metrics
        time_metrics = re.findall(r'\d+\s*(?:hours?|minutes?|days?|weeks?|months?)', text, re.IGNORECASE)
        metrics.extend(time_metrics)
        
        # Find money metrics
        money_metrics = re.findall(r'\$[\d,]+', text)
        metrics.extend(money_metrics)
        
        # Find general numbers with context
        number_contexts = re.findall(r'(\d+)\s+(\w+)', text)
        for num, context in number_contexts:
            if context.lower() not in ['the', 'a', 'an', 'and', 'or', 'of']:
                metrics.append(f"{num} {context}")
        
        return list(set(metrics))[:10]
    def _extract_competitors(self, text: str) -> List[str]:
        """Extract competitor mentions"""
        # Common competitor indicators
        competitor_patterns = [
            r'(?:use|used|using|tried|trying|switch from|switched from|instead of)\s+(\w+)',
            r'(\w+)\s+(?:is better|works better|is easier)',
            r'compared to\s+(\w+)',
            r'like\s+(\w+)',
            r'similar to\s+(\w+)',
        ]
        
        competitors = set()
        for pattern in competitor_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            competitors.update(matches)
        
        # Filter out common words
        common_words = {'this', 'that', 'it', 'them', 'other', 'another', 'something'}
        competitors = [c for c in competitors if c.lower() not in common_words and len(c) > 2]
        
        return list(competitors)[:5]
    def _assess_severity(self, text: str) -> str:
        """Assess severity of pain point"""
        if any(word in text for word in ['very', 'extremely', 'really', 'totally', 'completely']):
            return 'high'
        elif any(word in text for word in ['somewhat', 'bit', 'little', 'slightly']):
            return 'low'
        return 'medium'
    def _assess_strength(self, text: str) -> str:
        """Assess strength of positive feedback"""
        if any(word in text for word in ['absolutely', 'definitely', 'really', 'very']):
            return 'strong'
        return 'moderate'
    def _classify_request(self, text: str) -> str:
        """Classify the type of request"""
        if any(word in text for word in ['ui', 'design', 'look', 'color', 'layout']):
            return 'ui_improvement'
        elif any(word in text for word in ['feature', 'add', 'new', 'build']):
            return 'new_feature'
        elif any(word in text for word in ['fix', 'bug', 'broken', 'work']):
            return 'bug_fix'
        elif any(word in text for word in ['faster', 'slow', 'performance', 'speed']):
            return 'performance'
        return 'general'
    def _assess_request_priority(self, text: str) -> str:
        """Assess priority of request"""
        if any(word in text for word in ['critical', 'urgent', 'asap', 'immediately', 'blocking']):
            return 'critical'
        elif any(word in text for word in ['need', 'important', 'should', 'must']):
            return 'high'
        elif any(word in text for word in ['nice', 'would', 'could', 'maybe']):
            return 'low'
        return 'medium'
