# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from sprint_health_scorer_base import *  # noqa: F403,E402


HEALTH_DIMENSIONS = {
    "commitment_reliability": {
        "weight": 0.25,
        "excellent_threshold": 0.95,  # 95%+ commitment achievement
        "good_threshold": 0.85,       # 85%+ commitment achievement
        "poor_threshold": 0.70,       # Below 70% is poor
    },
    "scope_stability": {
        "weight": 0.20,
        "excellent_threshold": 0.05,  # ≤5% scope change
        "good_threshold": 0.15,       # ≤15% scope change
        "poor_threshold": 0.30,       # >30% scope change is poor
    },
    "blocker_resolution": {
        "weight": 0.15,
        "excellent_threshold": 1.0,   # ≤1 day average resolution
        "good_threshold": 3.0,        # ≤3 days average resolution
        "poor_threshold": 7.0,        # >7 days is poor
    },
    "ceremony_engagement": {
        "weight": 0.15,
        "excellent_threshold": 0.95,  # 95%+ attendance
        "good_threshold": 0.85,       # 85%+ attendance
        "poor_threshold": 0.70,       # Below 70% is poor
    },
    "story_completion_distribution": {
        "weight": 0.15,
        "excellent_threshold": 0.80,  # 80%+ stories fully completed
        "good_threshold": 0.65,       # 65%+ stories completed
        "poor_threshold": 0.50,       # Below 50% is poor
    },
    "velocity_predictability": {
        "weight": 0.10,
        "excellent_threshold": 0.10,  # ≤10% CV
        "good_threshold": 0.20,       # ≤20% CV
        "poor_threshold": 0.35,       # >35% CV is poor
    }
}
OVERALL_HEALTH_THRESHOLDS = {
    "excellent": 85,
    "good": 70,
    "fair": 55,
    "poor": 40,
}
STORY_STATUS_MAPPING = {
    "completed": ["done", "completed", "closed", "resolved"],
    "in_progress": ["in progress", "in_progress", "development", "testing"],
    "blocked": ["blocked", "impediment", "waiting"],
    "not_started": ["todo", "to do", "backlog", "new", "open"],
}
class Story:
    """Represents a user story within a sprint."""
    
    def __init__(self, data: Dict[str, Any]):
        self.id: str = data.get("id", "")
        self.title: str = data.get("title", "")
        self.points: int = data.get("points", 0)
        self.status: str = data.get("status", "").lower()
        self.assigned_to: str = data.get("assigned_to", "")
        self.created_date: str = data.get("created_date", "")
        self.completed_date: Optional[str] = data.get("completed_date")
        self.blocked_days: int = data.get("blocked_days", 0)
        self.priority: str = data.get("priority", "medium")
        
        # Normalize status
        self.normalized_status = self._normalize_status(self.status)
    
    def _normalize_status(self, status: str) -> str:
        """Normalize status to standard categories."""
        status_lower = status.lower().strip()
        
        for category, statuses in STORY_STATUS_MAPPING.items():
            if status_lower in statuses:
                return category
        
        return "unknown"
    
    @property
    def is_completed(self) -> bool:
        return self.normalized_status == "completed"
    
    @property
    def is_blocked(self) -> bool:
        return self.normalized_status == "blocked" or self.blocked_days > 0
