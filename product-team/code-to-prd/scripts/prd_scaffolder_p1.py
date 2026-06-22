# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from prd_scaffolder_base import *  # noqa: F403,E402


def slugify(text: str) -> str:
    """Convert text to a filename-safe slug."""
    text = text.strip().lower()
    text = re.sub(r"[/:{}*?\"<>|]", "-", text)
    text = re.sub(r"[^a-z0-9\-]", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")
def route_to_page_name(route: str) -> str:
    """Convert a route path to a human-readable page name."""
    if route == "/" or route == "":
        return "Home"
    parts = route.strip("/").split("/")
    # Remove dynamic segments for naming
    clean = [p for p in parts if not p.startswith(":") and not p.startswith("*")]
    if not clean:
        clean = [p.lstrip(":*") for p in parts]
    return " ".join(w.capitalize() for w in "-".join(clean).replace("_", "-").split("-"))
def generate_readme(project_name: str, routes: List[Dict], summary: Dict, date: str) -> str:
    """Generate the PRD README.md."""
    lines = [
        f"# {project_name} — Product Requirements Document",
        "",
        f"> Generated: {date}",
        "",
        "## System Overview",
        "",
        f"<!-- TODO: Describe what {project_name} does, its business context, and primary users -->",
        "",
        "## Summary",
        "",
        f"| Metric | Count |",
        f"|--------|-------|",
        f"| Pages | {summary.get('pages', 0)} |",
        f"| API Endpoints | {summary.get('api_endpoints', 0)} |",
        f"| Integrated APIs | {summary.get('api_integrated', 0)} |",
        f"| Mock APIs | {summary.get('api_mock', 0)} |",
        f"| Enums/Constants | {summary.get('enums', 0)} |",
        f"| i18n | {'Yes' if summary.get('has_i18n') else 'No'} |",
        f"| State Management | {'Yes' if summary.get('has_state_management') else 'No'} |",
        "",
        "## Module Overview",
        "",
        "| Module | Pages | Core Functionality |",
        "|--------|-------|--------------------|",
        "| <!-- TODO: Group pages into modules --> | | |",
        "",
        "## Page Inventory",
        "",
        "| # | Page Name | Route | Module | Doc Link |",
        "|---|-----------|-------|--------|----------|",
    ]

    for i, route in enumerate(routes, 1):
        path = route.get("path", "/")
        name = route_to_page_name(path)
        slug = slugify(name) or f"page-{i}"
        filename = f"{i:02d}-{slug}.md"
        lines.append(f"| {i} | {name} | `{path}` | <!-- TODO --> | [→](./pages/{filename}) |")

    lines.extend([
        "",
        "## Global Notes",
        "",
        "### Permission Model",
        "<!-- TODO: Summarize auth/role system if present -->",
        "",
        "### Common Interaction Patterns",
        "<!-- TODO: Global rules — delete confirmations, default sort, etc. -->",
        "",
    ])

    return "\n".join(lines)
