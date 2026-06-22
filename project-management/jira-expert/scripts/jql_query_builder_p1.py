# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from jql_query_builder_base import *  # noqa: F403,E402


PATTERN_LIBRARY = {
    "my_open_bugs": {
        "phrases": ["my open bugs", "my bugs", "bugs assigned to me"],
        "jql": 'assignee = currentUser() AND type = Bug AND status != Done',
        "description": "All open bugs assigned to current user",
    },
    "high_priority_bugs": {
        "phrases": ["high priority bugs", "critical bugs", "urgent bugs", "p1 bugs"],
        "jql": 'type = Bug AND priority in (Highest, High) AND status != Done',
        "description": "High and highest priority open bugs",
    },
    "my_open_tasks": {
        "phrases": ["my open tasks", "my tasks", "tasks assigned to me", "my work"],
        "jql": 'assignee = currentUser() AND status != Done',
        "description": "All open issues assigned to current user",
    },
    "unassigned_issues": {
        "phrases": ["unassigned", "unassigned issues", "no assignee"],
        "jql": 'assignee is EMPTY AND status != Done',
        "description": "Issues with no assignee",
    },
    "recently_created": {
        "phrases": ["recently created", "new issues", "created this week", "recent"],
        "jql": 'created >= -7d ORDER BY created DESC',
        "description": "Issues created in the last 7 days",
    },
    "recently_updated": {
        "phrases": ["recently updated", "updated this week", "recent changes"],
        "jql": 'updated >= -7d ORDER BY updated DESC',
        "description": "Issues updated in the last 7 days",
    },
    "overdue": {
        "phrases": ["overdue", "past due", "missed deadline", "overdue tasks"],
        "jql": 'duedate < now() AND status != Done',
        "description": "Issues past their due date",
    },
    "due_this_week": {
        "phrases": ["due this week", "due soon", "upcoming deadlines"],
        "jql": 'duedate >= startOfWeek() AND duedate <= endOfWeek() AND status != Done',
        "description": "Issues due this week",
    },
    "blocked_issues": {
        "phrases": ["blocked", "blocked issues", "impediments"],
        "jql": 'status = Blocked OR status = Impediment',
        "description": "Issues in blocked or impediment status",
    },
    "in_progress": {
        "phrases": ["in progress", "being worked on", "active work"],
        "jql": 'status = "In Progress"',
        "description": "Issues currently in progress",
    },
    "sprint_issues": {
        "phrases": ["current sprint", "this sprint", "active sprint"],
        "jql": 'sprint in openSprints()',
        "description": "Issues in the current active sprint",
    },
    "backlog": {
        "phrases": ["backlog", "backlog items", "not started"],
        "jql": 'sprint is EMPTY AND status = "To Do" ORDER BY priority DESC',
        "description": "Issues in the backlog not assigned to a sprint",
    },
    "stories_without_estimates": {
        "phrases": ["no estimates", "unestimated", "missing estimates", "no story points"],
        "jql": 'type = Story AND (storyPoints is EMPTY OR storyPoints = 0) AND status != Done',
        "description": "Stories missing story point estimates",
    },
    "epics_in_progress": {
        "phrases": ["active epics", "epics in progress", "open epics"],
        "jql": 'type = Epic AND status != Done ORDER BY priority DESC',
        "description": "Epics that are not yet completed",
    },
    "done_this_week": {
        "phrases": ["done this week", "completed this week", "resolved this week"],
        "jql": 'status changed to Done DURING (startOfWeek(), now())',
        "description": "Issues completed during the current week",
    },
    "created_vs_resolved": {
        "phrases": ["created vs resolved", "issue flow", "throughput"],
        "jql": 'created >= -30d ORDER BY created DESC',
        "description": "Issues created in the last 30 days for flow analysis",
    },
    "my_reported_issues": {
        "phrases": ["my reported", "reported by me", "i created", "i reported"],
        "jql": 'reporter = currentUser() ORDER BY created DESC',
        "description": "Issues reported by current user",
    },
    "stale_issues": {
        "phrases": ["stale", "stale issues", "not updated", "abandoned"],
        "jql": 'updated <= -30d AND status != Done ORDER BY updated ASC',
        "description": "Issues not updated in 30+ days",
    },
    "subtasks_without_parent": {
        "phrases": ["orphan subtasks", "subtasks no parent", "loose subtasks"],
        "jql": 'type = Sub-task AND parent is EMPTY',
        "description": "Subtasks missing parent issues",
    },
    "high_priority_unassigned": {
        "phrases": ["high priority unassigned", "urgent unassigned", "critical no owner"],
        "jql": 'priority in (Highest, High) AND assignee is EMPTY AND status != Done',
        "description": "High priority issues with no assignee",
    },
    "bugs_by_component": {
        "phrases": ["bugs by component", "component bugs"],
        "jql": 'type = Bug AND status != Done ORDER BY component ASC',
        "description": "Open bugs organized by component",
    },
    "resolved_recently": {
        "phrases": ["resolved recently", "recently resolved", "fixed this month"],
        "jql": 'resolved >= -30d ORDER BY resolved DESC',
        "description": "Issues resolved in the last 30 days",
    },
}
