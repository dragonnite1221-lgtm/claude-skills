# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from jql_query_builder_base import *  # noqa: F403,E402
# fmt: off
from jql_query_builder_p2 import ASSIGNEE_PATTERN, COMPONENT_PATTERN, DATE_RANGE_PATTERN, KEYWORD_FRAGMENTS, LABEL_PATTERN, SPRINT_NAME_PATTERN, _extract_project, find_matching_pattern  # noqa: E402,E501
# fmt: on


def build_jql_from_description(description: str) -> Dict[str, Any]:
    """Build JQL query from natural language description."""
    # First try exact pattern match
    pattern_match = find_matching_pattern(description)
    if pattern_match:
        # Augment with project if mentioned
        project = _extract_project(description)
        if project:
            pattern_match["jql"] = f'project = {project} AND {pattern_match["jql"]}'
        return pattern_match

    # Dynamic query building
    clauses = []
    used_fields = set()
    desc_lower = description.lower()

    # Extract project
    project = _extract_project(description)
    if project:
        clauses.append(f"project = {project}")
        used_fields.add("project")

    # Extract keyword-based fragments
    for keyword, (field, fragment) in KEYWORD_FRAGMENTS.items():
        if keyword in desc_lower.split() and field not in used_fields:
            clauses.append(f"{field} {fragment}")
            used_fields.add(field)

    # Extract explicit assignee
    assignee_match = ASSIGNEE_PATTERN.search(description)
    if assignee_match and "assignee" not in used_fields:
        assignee = assignee_match.group(1)
        if assignee.lower() in ("me", "myself"):
            clauses.append("assignee = currentUser()")
        else:
            clauses.append(f'assignee = "{assignee}"')
        used_fields.add("assignee")

    # Extract labels
    label_match = LABEL_PATTERN.search(description)
    if label_match:
        clauses.append(f'labels = "{label_match.group(1)}"')

    # Extract component
    component_match = COMPONENT_PATTERN.search(description)
    if component_match:
        clauses.append(f'component = "{component_match.group(1)}"')

    # Extract date ranges
    date_match = DATE_RANGE_PATTERN.search(description)
    if date_match:
        amount = date_match.group(1)
        unit = date_match.group(2).lower()
        unit_char = {"day": "d", "week": "w", "month": "m"}.get(unit, "d")
        clauses.append(f"created >= -{amount}{unit_char}")

    # Extract sprint reference
    sprint_match = SPRINT_NAME_PATTERN.search(description)
    if sprint_match:
        sprint_name = sprint_match.group(1).strip()
        if sprint_name.lower() in ("current", "active", "open"):
            clauses.append("sprint in openSprints()")
        else:
            clauses.append(f'sprint = "{sprint_name}"')

    # Default: if no status clause and not looking for done items
    if "status" not in used_fields and "done" not in desc_lower and "closed" not in desc_lower:
        clauses.append("status != Done")

    if not clauses:
        return {
            "jql": "",
            "description": "Could not build query from description",
            "match_type": "no_match",
            "error": "No recognizable patterns found in description",
        }

    jql = " AND ".join(clauses)

    # Add ORDER BY for common scenarios
    if "recent" in desc_lower or "latest" in desc_lower:
        jql += " ORDER BY created DESC"
    elif "priority" in desc_lower or "urgent" in desc_lower:
        jql += " ORDER BY priority DESC"

    return {
        "jql": jql,
        "description": f"Dynamic query from: {description}",
        "match_type": "dynamic",
        "clauses_used": len(clauses),
    }
