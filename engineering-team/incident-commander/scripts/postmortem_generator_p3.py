# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from postmortem_generator_base import *  # noqa: F403,E402
# fmt: off
from postmortem_generator_p1 import ACTION_TYPES, PRIORITY_ORDER  # noqa: E402,E501
# fmt: on


class ActionItem:
    """Parsed and validated action item."""
    def __init__(self, data: Dict[str, Any]) -> None:
        self.title: str = data.get("title", "")
        self.owner: str = data.get("owner", "")
        self.priority: str = data.get("priority", "P3")
        self.deadline: str = data.get("deadline", "")
        self.type: str = data.get("type", "process")
        self.status: str = data.get("status", "open")
        self.validation_issues: List[str] = []
        self.quality_score: int = 0
        self._validate()

    def _validate(self) -> None:
        self.validation_issues = []
        if not self.title:
            self.validation_issues.append("Missing title")
        if not self.owner:
            self.validation_issues.append("Missing owner")
        if not self.deadline:
            self.validation_issues.append("Missing deadline")
        if self.priority not in PRIORITY_ORDER:
            self.validation_issues.append(f"Invalid priority: {self.priority}")
        if self.type not in ACTION_TYPES:
            self.validation_issues.append(f"Invalid type: {self.type}")
        self.quality_score = self._score_quality()

    def _score_quality(self) -> int:
        """Score 0-100: specific, measurable, achievable."""
        s = 0
        if len(self.title) > 10: s += 20
        if self.owner: s += 20
        if self.deadline: s += 20
        if self.priority in PRIORITY_ORDER: s += 10
        if self.type in ACTION_TYPES: s += 10
        if any(kw in self.title.lower() for kw in ["%", "threshold", "within", "before",
                                                     "after", "less than", "greater than"]):
            s += 10
        if len(self.title.split()) >= 5: s += 10
        return min(s, 100)

    @property
    def is_valid(self) -> bool:
        return len(self.validation_issues) == 0

    @property
    def is_past_deadline(self) -> bool:
        if not self.deadline or self.status != "open":
            return False
        try:
            dl = datetime.strptime(self.deadline, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            return datetime.now(timezone.utc) > dl
        except ValueError:
            return False

    def to_dict(self) -> Dict[str, Any]:
        return {"title": self.title, "owner": self.owner, "priority": self.priority,
                "deadline": self.deadline, "type": self.type, "status": self.status,
                "is_valid": self.is_valid, "validation_issues": self.validation_issues,
                "quality_score": self.quality_score, "is_past_deadline": self.is_past_deadline}
