# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from retrospective_analyzer_base import *  # noqa: F403,E402


SENTIMENT_KEYWORDS = {
    "positive": [
        "good", "great", "excellent", "awesome", "fantastic", "wonderful",
        "improved", "better", "success", "achievement", "celebration",
        "working well", "effective", "efficient", "smooth", "pleased",
        "happy", "satisfied", "proud", "accomplished", "breakthrough"
    ],
    "negative": [
        "bad", "terrible", "awful", "horrible", "frustrating", "annoying",
        "problem", "issue", "blocker", "impediment", "concern", "worry",
        "difficult", "challenging", "struggling", "failing", "broken",
        "slow", "delayed", "confused", "unclear", "chaos", "stressed"
    ],
    "neutral": [
        "okay", "average", "normal", "standard", "typical", "usual",
        "process", "procedure", "meeting", "discussion", "review",
        "update", "status", "information", "data", "report"
    ]
}
THEME_CATEGORIES = {
    "communication": [
        "communication", "meeting", "standup", "discussion", "feedback",
        "information", "clarity", "understanding", "alignment", "sync",
        "reporting", "updates", "transparency", "visibility"
    ],
    "process": [
        "process", "procedure", "workflow", "methodology", "framework",
        "scrum", "agile", "ceremony", "planning", "retrospective",
        "review", "estimation", "refinement", "definition of done"
    ],
    "technical": [
        "technical", "code", "development", "bug", "testing", "deployment",
        "architecture", "infrastructure", "tools", "technology",
        "performance", "quality", "automation", "ci/cd", "devops"
    ],
    "team_dynamics": [
        "team", "collaboration", "cooperation", "support", "morale",
        "motivation", "engagement", "culture", "relationship", "trust",
        "conflict", "personality", "workload", "capacity", "burnout"
    ],
    "external": [
        "customer", "stakeholder", "management", "product owner", "business",
        "requirement", "priority", "deadline", "budget", "resource",
        "dependency", "vendor", "third party", "integration"
    ]
}
ACTION_PRIORITY_KEYWORDS = {
    "high": ["urgent", "critical", "asap", "immediately", "blocker", "must"],
    "medium": ["important", "should", "needed", "required", "significant"],
    "low": ["nice to have", "consider", "explore", "investigate", "eventually"]
}
COMPLETION_STATUS_MAPPING = {
    "completed": ["done", "completed", "finished", "resolved", "closed", "achieved"],
    "in_progress": ["in progress", "ongoing", "working on", "started", "partial"],
    "blocked": ["blocked", "stuck", "waiting", "dependent", "impediment"],
    "cancelled": ["cancelled", "dropped", "abandoned", "not needed", "deprioritized"],
    "not_started": ["not started", "pending", "todo", "planned", "upcoming"]
}
class ActionItem:
    """Represents a single action item from a retrospective."""
    
    def __init__(self, data: Dict[str, Any]):
        self.id: str = data.get("id", "")
        self.description: str = data.get("description", "")
        self.owner: str = data.get("owner", "")
        self.priority: str = data.get("priority", "medium").lower()
        self.due_date: Optional[str] = data.get("due_date")
        self.status: str = data.get("status", "not_started").lower()
        self.created_sprint: int = data.get("created_sprint", 0)
        self.completed_sprint: Optional[int] = data.get("completed_sprint")
        self.category: str = data.get("category", "")
        self.effort_estimate: str = data.get("effort_estimate", "medium")
        
        # Normalize status
        self.normalized_status = self._normalize_status(self.status)
        
        # Infer priority from description if not explicitly set
        if self.priority == "medium":
            self.inferred_priority = self._infer_priority(self.description)
        else:
            self.inferred_priority = self.priority
    
    def _normalize_status(self, status: str) -> str:
        """Normalize status to standard categories."""
        status_lower = status.lower().strip()
        
        for category, statuses in COMPLETION_STATUS_MAPPING.items():
            if any(s in status_lower for s in statuses):
                return category
        
        return "not_started"
    
    def _infer_priority(self, description: str) -> str:
        """Infer priority from description text."""
        description_lower = description.lower()
        
        for priority, keywords in ACTION_PRIORITY_KEYWORDS.items():
            if any(keyword in description_lower for keyword in keywords):
                return priority
        
        return "medium"
    
    @property
    def is_completed(self) -> bool:
        return self.normalized_status == "completed"
    
    @property
    def is_overdue(self) -> bool:
        if not self.due_date:
            return False
        
        try:
            due_date = datetime.strptime(self.due_date, "%Y-%m-%d")
            return datetime.now() > due_date and not self.is_completed
        except ValueError:
            return False
