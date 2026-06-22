# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from quality_scorer_base import *  # noqa: F403,E402


try:
    import yaml
except ImportError:
    # Minimal YAML subset: parse simple key: value frontmatter without pyyaml
    class _YamlStub:
        class YAMLError(Exception):
            pass
        @staticmethod
        def safe_load(text):
            result = {}
            for line in text.strip().splitlines():
                if ':' in line:
                    key, _, value = line.partition(':')
                    result[key.strip()] = value.strip()
            return result if result else None
    yaml = _YamlStub()


class QualityDimension:
    """Represents a quality scoring dimension"""
    
    def __init__(self, name: str, weight: float, description: str):
        self.name = name
        self.weight = weight
        self.description = description
        self.score = 0.0
        self.max_score = 100.0
        self.details = {}
        self.suggestions = []
        
    def add_score(self, component: str, score: float, max_score: float, details: str = ""):
        """Add a component score"""
        self.details[component] = {
            "score": score,
            "max_score": max_score,
            "percentage": (score / max_score * 100) if max_score > 0 else 0,
            "details": details
        }
        
    def calculate_final_score(self):
        """Calculate the final weighted score for this dimension"""
        if not self.details:
            self.score = 0.0
            return
            
        total_score = sum(detail["score"] for detail in self.details.values())
        total_max = sum(detail["max_score"] for detail in self.details.values())
        
        self.score = (total_score / total_max * 100) if total_max > 0 else 0.0
        
    def add_suggestion(self, suggestion: str):
        """Add an improvement suggestion"""
        self.suggestions.append(suggestion)
