# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from agent_evaluator_base import *  # noqa: F403,E402


class AgentEvaluatorMixin4:
    def _extract_common_patterns(self, error_messages: List[str]) -> List[str]:
        """Extract common patterns from error messages"""
        if not error_messages:
            return []
        
        # Simple pattern extraction - find common phrases
        word_counts = Counter()
        for message in error_messages:
            words = re.findall(r'\w+', message.lower())
            for word in words:
                if len(word) > 3:  # Ignore short words
                    word_counts[word] += 1
        
        # Return most common words/patterns
        common_patterns = [word for word, count in word_counts.most_common(5) 
                          if count > 1]
        
        return common_patterns
