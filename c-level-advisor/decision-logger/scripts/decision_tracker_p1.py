# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from decision_tracker_base import *  # noqa: F403,E402


class ActionItem:
    def __init__(self, text: str, owner: str, due: Optional[date],
                 review: Optional[date], completed: bool, completed_date: Optional[date],
                 result: str):
        self.text = text
        self.owner = owner
        self.due = due
        self.review = review
        self.completed = completed
        self.completed_date = completed_date
        self.result = result

    def is_overdue(self) -> bool:
        if self.completed:
            return False
        if self.due and self.due < date.today():
            return True
        return False

    def is_due_within(self, days: int) -> bool:
        if self.completed:
            return False
        if self.due:
            return date.today() <= self.due <= date.today() + timedelta(days=days)
        return False
class Decision:
    def __init__(self):
        self.date: Optional[date] = None
        self.title: str = ""
        self.decision: str = ""
        self.owner: str = ""
        self.deadline: Optional[date] = None
        self.review: Optional[date] = None
        self.rationale: str = ""
        self.user_override: str = ""
        self.rejected: list[str] = []
        self.action_items: list[ActionItem] = []
        self.supersedes: str = ""
        self.superseded_by: str = ""
        self.raw_transcript: str = ""

    def is_active(self) -> bool:
        return not bool(self.superseded_by.strip())

    def has_override(self) -> bool:
        return bool(self.user_override.strip())
def parse_date(s: str) -> Optional[date]:
    """Parse YYYY-MM-DD or return None."""
    if not s:
        return None
    s = s.strip()
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d.%m.%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None
def parse_action_item(line: str) -> Optional[ActionItem]:
    """
    Parse a line like:
      - [ ] Action text — Owner: CMO — Due: 2026-03-15 — Review: 2026-03-29
      - [x] Action text — Owner: CEO — Completed: 2026-03-10 — Result: Done
    """
    line = line.strip()
    if not line.startswith("- ["):
        return None

    completed = line.startswith("- [x]") or line.startswith("- [X]")
    text_start = line.find("]") + 1
    raw = line[text_start:].strip()

    # Split on " — " (em dash with spaces) or " - " fallback
    parts_raw = re.split(r"\s+[—\-]{1,2}\s+", raw)
    text = parts_raw[0].strip() if parts_raw else raw

    def extract(label: str, parts: list[str]) -> str:
        for p in parts:
            if p.lower().startswith(label.lower() + ":"):
                return p[len(label) + 1:].strip()
        return ""

    owner = extract("Owner", parts_raw[1:])
    due_str = extract("Due", parts_raw[1:])
    review_str = extract("Review", parts_raw[1:])
    completed_str = extract("Completed", parts_raw[1:])
    result = extract("Result", parts_raw[1:])

    return ActionItem(
        text=text,
        owner=owner,
        due=parse_date(due_str),
        review=parse_date(review_str),
        completed=completed,
        completed_date=parse_date(completed_str),
        result=result,
    )
