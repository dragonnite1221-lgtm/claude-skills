# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from space_structure_generator_base import *  # noqa: F403,E402


PERMISSION_TEMPLATES = {
    "engineering": {
        "admins": ["team-leads", "engineering-managers"],
        "contributors": ["developers", "qa-engineers"],
        "viewers": ["product-team", "stakeholders"],
        "restrictions": [
            "Restrict 'Runbooks' section to engineering team only",
            "Allow product team view-only access to Architecture",
        ],
    },
    "product": {
        "admins": ["product-managers", "product-leads"],
        "contributors": ["product-designers", "product-analysts"],
        "viewers": ["engineering-team", "marketing-team", "stakeholders"],
        "restrictions": [
            "Restrict 'Research' raw data to product team only",
            "Share 'Strategy' with leadership and stakeholders",
        ],
    },
    "marketing": {
        "admins": ["marketing-managers", "marketing-leads"],
        "contributors": ["content-creators", "designers"],
        "viewers": ["sales-team", "product-team"],
        "restrictions": [
            "Restrict campaign budgets to marketing leadership",
            "Share brand guidelines broadly",
        ],
    },
    "project": {
        "admins": ["project-managers"],
        "contributors": ["project-team-members"],
        "viewers": ["stakeholders", "sponsors"],
        "restrictions": [
            "Restrict 'Budget & Financials' to project managers and sponsors",
            "Share status reports with all stakeholders",
        ],
    },
}
def _deep_copy_section(section: Dict[str, Any]) -> Dict[str, Any]:
    """Create a deep copy of a section dict."""
    copy = {
        "title": section["title"],
        "labels": list(section.get("labels", [])),
    }
    if "description" in section:
        copy["description"] = section["description"]
    if "children" in section:
        copy["children"] = [_deep_copy_section(child) for child in section["children"]]
    return copy
def _slugify(text: str) -> str:
    """Convert text to a URL-safe slug."""
    return text.lower().replace(" ", "-").replace("_", "-")
def _generate_space_key(team_name: str) -> str:
    """Generate a space key from team name."""
    words = team_name.upper().split()
    if len(words) == 1:
        return words[0][:10]
    return "".join(w[0] for w in words[:5])
def _collect_labels(pages: List[Dict], labels: set) -> None:
    """Recursively collect all labels from page tree."""
    for page in pages:
        for label in page.get("labels", []):
            labels.add(label)
        children = page.get("children", [])
        if children:
            _collect_labels(children, labels)
def _count_pages(pages: List[Dict]) -> int:
    """Count total pages in tree."""
    count = len(pages)
    for page in pages:
        children = page.get("children", [])
        if children:
            count += _count_pages(children)
    return count
def _generate_recommendations(
    team_name: str,
    team_type: str,
    team_size: int,
    projects: List,
) -> List[str]:
    """Generate setup recommendations."""
    recs = []

    recs.append(f"Create the space with key '{_generate_space_key(team_name)}' and enable the blog feature for announcements.")

    if team_size > 10:
        recs.append("Large team detected. Consider sub-spaces or restricted sections for sub-teams.")

    if team_size <= 3:
        recs.append("Small team. Simplify the structure by merging low-traffic sections.")

    if len(projects) > 5:
        recs.append("Many projects listed. Consider a separate space per project for better isolation.")

    if team_type == "engineering":
        recs.append("Set up page templates for ADRs, runbooks, and design docs.")
        recs.append("Enable the Jira macro on Architecture pages for traceability.")
    elif team_type == "product":
        recs.append("Set up page templates for feature specs and user research notes.")
        recs.append("Link roadmap pages to Jira epics for real-time status.")
    elif team_type == "marketing":
        recs.append("Enable the calendar macro on the Content Calendar page.")
        recs.append("Use labels consistently to enable filtered content views.")

    recs.append("Review and update space permissions quarterly.")
    recs.append("Archive pages older than 6 months that are no longer actively referenced.")

    return recs
