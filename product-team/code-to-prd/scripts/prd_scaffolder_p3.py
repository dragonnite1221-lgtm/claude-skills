# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from prd_scaffolder_base import *  # noqa: F403,E402
# fmt: off
from prd_scaffolder_p1 import generate_readme, route_to_page_name, slugify  # noqa: E402,E501
from prd_scaffolder_p2 import generate_api_inventory, generate_enum_dictionary, generate_page_stub  # noqa: E402,E501
# fmt: on


def generate_page_relationships(routes: List[Dict]) -> str:
    """Generate page relationships appendix stub."""
    lines = [
        "# Page Relationships",
        "",
        "Navigation flow and data coupling between pages.",
        "",
        "## Navigation Map",
        "",
        "<!-- TODO: Fill in after page-by-page analysis -->",
        "",
        "```",
        "Home",
    ]

    for r in routes[:20]:  # Cap at 20 for readability
        name = route_to_page_name(r.get("path", "/"))
        lines.append(f"  ├── {name}")

    if len(routes) > 20:
        lines.append(f"  └── ... ({len(routes) - 20} more)")

    lines.extend([
        "```",
        "",
        "## Cross-Page Data Dependencies",
        "",
        "| Source Page | Target Page | Trigger | Data Passed |",
        "|-----------|------------|---------|------------|",
        "| <!-- TODO --> | | | |",
        "",
    ])

    return "\n".join(lines)
def scaffold(analysis: Dict[str, Any], output_dir: Path, project_name: Optional[str] = None):
    """Create the full PRD directory structure."""
    date = datetime.now().strftime("%Y-%m-%d")
    name = project_name or analysis.get("project", {}).get("name", "Project")
    routes = analysis.get("routes", {}).get("pages", [])
    apis = analysis.get("apis", {}).get("endpoints", [])
    enums = analysis.get("enums", {}).get("definitions", [])
    summary = analysis.get("summary", {})

    # Create directories
    pages_dir = output_dir / "pages"
    appendix_dir = output_dir / "appendix"
    pages_dir.mkdir(parents=True, exist_ok=True)
    appendix_dir.mkdir(parents=True, exist_ok=True)

    # README.md
    readme = generate_readme(name, routes, summary, date)
    (output_dir / "README.md").write_text(readme)
    print(f"  Created: README.md")

    # Per-page stubs
    for i, route in enumerate(routes, 1):
        page_name = route_to_page_name(route.get("path", "/"))
        slug = slugify(page_name) or f"page-{i}"
        filename = f"{i:02d}-{slug}.md"
        content = generate_page_stub(route, i, date)
        (pages_dir / filename).write_text(content)
        print(f"  Created: pages/{filename}")

    # Appendix
    (appendix_dir / "enum-dictionary.md").write_text(generate_enum_dictionary(enums))
    print(f"  Created: appendix/enum-dictionary.md")

    (appendix_dir / "api-inventory.md").write_text(generate_api_inventory(apis))
    print(f"  Created: appendix/api-inventory.md")

    (appendix_dir / "page-relationships.md").write_text(generate_page_relationships(routes))
    print(f"  Created: appendix/page-relationships.md")

    print(f"\n✅ PRD scaffold complete: {output_dir}")
    print(f"   {len(routes)} page stubs, {len(apis)} API endpoints, {len(enums)} enums")
    print(f"\n   Next: Review each page stub and fill in the TODO sections.")
def validate_analysis(analysis: Dict[str, Any]) -> List[str]:
    """Validate analysis JSON has the required structure. Returns list of errors."""
    errors = []

    if not isinstance(analysis, dict):
        return ["Analysis must be a JSON object"]

    if "error" in analysis:
        errors.append(f"Analysis contains error: {analysis['error']}")

    required_keys = ["project", "routes", "apis"]
    for key in required_keys:
        if key not in analysis:
            errors.append(f"Missing required key: '{key}'")

    if "project" in analysis:
        proj = analysis["project"]
        if not isinstance(proj, dict):
            errors.append("'project' must be an object")
        elif "framework" not in proj:
            errors.append("'project.framework' is missing")

    if "routes" in analysis:
        routes = analysis["routes"]
        if not isinstance(routes, dict):
            errors.append("'routes' must be an object")
        elif "pages" not in routes and "frontend_pages" not in routes and "backend_endpoints" not in routes:
            errors.append("'routes' must contain 'pages', 'frontend_pages', or 'backend_endpoints'")

    if "apis" in analysis:
        apis = analysis["apis"]
        if not isinstance(apis, dict):
            errors.append("'apis' must be an object")
        elif "endpoints" not in apis:
            errors.append("'apis.endpoints' is missing")

    return errors
def print_summary(output_dir: Path, analysis: Dict[str, Any]):
    """Print a structured summary of what was generated."""
    routes = analysis.get("routes", {}).get("pages", [])
    apis = analysis.get("apis", {}).get("endpoints", [])
    enums = analysis.get("enums", {}).get("definitions", [])
    models = analysis.get("models", {}).get("definitions", [])
    summary = analysis.get("summary", {})
    stack = summary.get("stack_type", "unknown")

    print(f"\nPRD scaffold complete: {output_dir}/")
    print(f"  Stack type:     {stack}")
    print(f"  Page stubs:     {len(routes)}")
    print(f"  API endpoints:  {len(apis)}")
    print(f"  Enums:          {len(enums)}")
    if models:
        print(f"  Models:         {len(models)}")
    print(f"\n  Next: Review each page stub and fill in the TODO sections.")
