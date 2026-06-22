# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from retrospective_analyzer_base import *  # noqa: F403,E402
# fmt: off
from retrospective_analyzer_p1 import ActionItem, SENTIMENT_KEYWORDS, THEME_CATEGORIES  # noqa: E402,E501
# fmt: on


class RetrospectiveData:
    """Represents data from a single retrospective session."""
    
    def __init__(self, data: Dict[str, Any]):
        self.sprint_number: int = data.get("sprint_number", 0)
        self.date: str = data.get("date", "")
        self.facilitator: str = data.get("facilitator", "")
        self.attendees: List[str] = data.get("attendees", [])
        self.duration_minutes: int = data.get("duration_minutes", 0)
        
        # Retrospective categories
        self.went_well: List[str] = data.get("went_well", [])
        self.to_improve: List[str] = data.get("to_improve", [])
        self.action_items_data: List[Dict[str, Any]] = data.get("action_items", [])
        
        # Create action items
        self.action_items: List[ActionItem] = [
            ActionItem({**item, "created_sprint": self.sprint_number})
            for item in self.action_items_data
        ]
        
        # Calculate metrics
        self._calculate_metrics()
    
    def _calculate_metrics(self):
        """Calculate retrospective session metrics."""
        self.total_items = len(self.went_well) + len(self.to_improve)
        self.action_items_count = len(self.action_items)
        self.attendance_rate = len(self.attendees) / max(1, 5)  # Assume team of 5
        
        # Sentiment analysis
        self.sentiment_scores = self._analyze_sentiment()
        
        # Theme analysis
        self.themes = self._extract_themes()
    
    def _analyze_sentiment(self) -> Dict[str, float]:
        """Analyze sentiment of retrospective items."""
        all_text = " ".join(self.went_well + self.to_improve).lower()
        
        sentiment_scores = {}
        for sentiment, keywords in SENTIMENT_KEYWORDS.items():
            count = sum(1 for keyword in keywords if keyword in all_text)
            sentiment_scores[sentiment] = count
        
        # Normalize to percentages
        total_sentiment = sum(sentiment_scores.values())
        if total_sentiment > 0:
            for sentiment in sentiment_scores:
                sentiment_scores[sentiment] = sentiment_scores[sentiment] / total_sentiment
        
        return sentiment_scores
    
    def _extract_themes(self) -> Dict[str, int]:
        """Extract themes from retrospective items."""
        all_text = " ".join(self.went_well + self.to_improve).lower()
        
        theme_counts = {}
        for theme, keywords in THEME_CATEGORIES.items():
            count = sum(1 for keyword in keywords if keyword in all_text)
            if count > 0:
                theme_counts[theme] = count
        
        return theme_counts
class RetroAnalysisResult:
    """Complete retrospective analysis results."""
    
    def __init__(self):
        self.summary: Dict[str, Any] = {}
        self.action_item_analysis: Dict[str, Any] = {}
        self.theme_analysis: Dict[str, Any] = {}
        self.improvement_trends: Dict[str, Any] = {}
        self.recommendations: List[str] = []
