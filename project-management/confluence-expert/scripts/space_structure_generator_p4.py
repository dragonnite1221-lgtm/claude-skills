# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from space_structure_generator_base import *  # noqa: F403,E402
# fmt: off
from space_structure_generator_p1 import BASE_SECTIONS  # noqa: E402,E501
from space_structure_generator_p2 import TEAM_TYPE_SECTIONS  # noqa: E402,E501
from space_structure_generator_p3 import PERMISSION_TEMPLATES, _collect_labels, _count_pages, _deep_copy_section, _generate_recommendations, _generate_space_key, _slugify  # noqa: E402,E501
# fmt: on


def generate_space_structure(team_info: Dict[str, Any]) -> Dict[str, Any]:
    """Generate Confluence space structure from team information."""
    team_name = team_info.get("name", "Team")
    team_type = team_info.get("type", "project").lower()
    team_size = team_info.get("size", 5)
    projects = team_info.get("projects", [])

    if team_type not in TEAM_TYPE_SECTIONS:
        team_type = "project"

    # Build page tree
    page_tree = []

    # Add base sections
    for section in BASE_SECTIONS:
        page_tree.append(_deep_copy_section(section))

    # Add team-type-specific sections
    type_sections = TEAM_TYPE_SECTIONS.get(team_type, [])
    for section in type_sections:
        page_tree.append(_deep_copy_section(section))

    # Add project-specific pages if projects are listed
    if projects:
        project_section = {
            "title": "Projects",
            "description": "Individual project documentation",
            "labels": ["projects"],
            "children": [],
        }
        for project in projects:
            project_name = project if isinstance(project, str) else project.get("name", "Project")
            project_section["children"].append({
                "title": project_name,
                "labels": ["project", _slugify(project_name)],
                "children": [
                    {"title": f"{project_name} - Overview", "labels": ["overview"]},
                    {"title": f"{project_name} - Requirements", "labels": ["requirements"]},
                    {"title": f"{project_name} - Status", "labels": ["status"]},
                ],
            })
        page_tree.append(project_section)

    # Get permissions
    permissions = PERMISSION_TEMPLATES.get(team_type, PERMISSION_TEMPLATES["project"])

    # Generate label taxonomy
    all_labels = set()
    _collect_labels(page_tree, all_labels)

    # Build recommendations
    recommendations = _generate_recommendations(team_name, team_type, team_size, projects)

    return {
        "space_key": _generate_space_key(team_name),
        "space_name": f"{team_name} Space",
        "team_type": team_type,
        "team_size": team_size,
        "page_tree": page_tree,
        "total_pages": _count_pages(page_tree),
        "labels": sorted(all_labels),
        "permissions": permissions,
        "recommendations": recommendations,
    }
def _format_page_tree(pages: List[Dict], indent: int = 0) -> List[str]:
    """Format page tree as indented text."""
    lines = []
    prefix = "  " * indent
    for page in pages:
        title = page["title"]
        labels = page.get("labels", [])
        label_str = f" [{', '.join(labels)}]" if labels else ""
        lines.append(f"{prefix}|- {title}{label_str}")
        if page.get("description"):
            lines.append(f"{prefix}   {page['description']}")
        children = page.get("children", [])
        if children:
            lines.extend(_format_page_tree(children, indent + 1))
    return lines
def format_text_output(result: Dict[str, Any]) -> str:
    """Format results as readable text report."""
    lines = []
    lines.append("=" * 60)
    lines.append("CONFLUENCE SPACE STRUCTURE")
    lines.append("=" * 60)
    lines.append("")

    lines.append("SPACE INFO")
    lines.append("-" * 30)
    lines.append(f"Space Name: {result['space_name']}")
    lines.append(f"Space Key: {result['space_key']}")
    lines.append(f"Team Type: {result['team_type'].title()}")
    lines.append(f"Team Size: {result['team_size']}")
    lines.append(f"Total Pages: {result['total_pages']}")
    lines.append("")

    lines.append("PAGE TREE")
    lines.append("-" * 30)
    lines.extend(_format_page_tree(result["page_tree"]))
    lines.append("")

    lines.append("LABELS")
    lines.append("-" * 30)
    lines.append(", ".join(result["labels"]))
    lines.append("")

    permissions = result.get("permissions", {})
    if permissions:
        lines.append("PERMISSION SUGGESTIONS")
        lines.append("-" * 30)
        lines.append(f"Admins: {', '.join(permissions.get('admins', []))}")
        lines.append(f"Contributors: {', '.join(permissions.get('contributors', []))}")
        lines.append(f"Viewers: {', '.join(permissions.get('viewers', []))}")
        for restriction in permissions.get("restrictions", []):
            lines.append(f"  - {restriction}")
        lines.append("")

    recommendations = result.get("recommendations", [])
    if recommendations:
        lines.append("RECOMMENDATIONS")
        lines.append("-" * 30)
        for i, rec in enumerate(recommendations, 1):
            lines.append(f"{i}. {rec}")

    return "\n".join(lines)
def format_json_output(result: Dict[str, Any]) -> Dict[str, Any]:
    """Format results as JSON."""
    return result
