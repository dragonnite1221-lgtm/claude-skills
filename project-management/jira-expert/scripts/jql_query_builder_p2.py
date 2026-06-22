# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from jql_query_builder_base import *  # noqa: F403,E402
# fmt: off
from jql_query_builder_p1 import PATTERN_LIBRARY  # noqa: E402,E501
# fmt: on


KEYWORD_FRAGMENTS = {
    # Issue types
    "bug": ("type", "= Bug"),
    "bugs": ("type", "= Bug"),
    "story": ("type", "= Story"),
    "stories": ("type", "= Story"),
    "task": ("type", "= Task"),
    "tasks": ("type", "= Task"),
    "epic": ("type", "= Epic"),
    "epics": ("type", "= Epic"),
    "subtask": ("type", "= Sub-task"),
    "sub-task": ("type", "= Sub-task"),
    # Statuses
    "open": ("status", "!= Done"),
    "closed": ("status", "= Done"),
    "done": ("status", "= Done"),
    "resolved": ("status", "= Done"),
    "todo": ("status", '= "To Do"'),
    # Priorities
    "critical": ("priority", "= Highest"),
    "highest": ("priority", "= Highest"),
    "high": ("priority", "in (Highest, High)"),
    "medium": ("priority", "= Medium"),
    "low": ("priority", "in (Low, Lowest)"),
    "lowest": ("priority", "= Lowest"),
    # Assignee
    "me": ("assignee", "= currentUser()"),
    "mine": ("assignee", "= currentUser()"),
    "unassigned": ("assignee", "is EMPTY"),
    # Time
    "overdue": ("duedate", "< now()"),
    "today": ("duedate", "= now()"),
}
PROJECT_PATTERN = re.compile(r'\b([A-Z]{2,10})\b')
ASSIGNEE_PATTERN = re.compile(r'assigned\s+to\s+(\w+)', re.IGNORECASE)
LABEL_PATTERN = re.compile(r'label[s]?\s*[=:]\s*["\']?(\w+)["\']?', re.IGNORECASE)
COMPONENT_PATTERN = re.compile(r'component[s]?\s*[=:]\s*["\']?(\w+)["\']?', re.IGNORECASE)
DATE_RANGE_PATTERN = re.compile(r'last\s+(\d+)\s+(day|week|month)s?', re.IGNORECASE)
SPRINT_NAME_PATTERN = re.compile(r'sprint\s+["\']?(\w[\w\s]*\w)["\']?', re.IGNORECASE)
EXCLUDED_WORDS = {
    "AND", "OR", "NOT", "IN", "IS", "TO", "BY", "ON", "DO", "BE",
    "THE", "ALL", "MY", "NO", "OF", "AT", "AS", "IF", "IT",
    "BUG", "BUGS", "TASK", "TASKS", "STORY", "EPIC", "DONE",
    "HIGH", "LOW", "MEDIUM", "JQL",
}
def find_matching_pattern(description: str) -> Optional[Dict[str, Any]]:
    """Check if description matches a known pattern exactly."""
    desc_lower = description.lower().strip()
    for pattern_name, pattern_data in PATTERN_LIBRARY.items():
        for phrase in pattern_data["phrases"]:
            if phrase in desc_lower or desc_lower in phrase:
                return {
                    "pattern_name": pattern_name,
                    "jql": pattern_data["jql"],
                    "description": pattern_data["description"],
                    "match_type": "exact_pattern",
                }
    return None
def _extract_project(description: str) -> Optional[str]:
    """Extract project key from description."""
    # Look for IN/in PROJECT pattern
    in_project = re.search(r'\bin\s+([A-Z]{2,10})\b', description)
    if in_project and in_project.group(1) not in EXCLUDED_WORDS:
        return in_project.group(1)

    # Look for standalone project keys
    for match in PROJECT_PATTERN.finditer(description):
        word = match.group(1)
        if word not in EXCLUDED_WORDS:
            return word

    return None
