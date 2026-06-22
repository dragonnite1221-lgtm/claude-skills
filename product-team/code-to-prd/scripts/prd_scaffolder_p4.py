# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from prd_scaffolder_base import *  # noqa: F403,E402
# fmt: off
from prd_scaffolder_p1 import route_to_page_name, slugify  # noqa: E402,E501
from prd_scaffolder_p3 import print_summary, scaffold, validate_analysis  # noqa: E402,E501
# fmt: on


def main():
    parser = argparse.ArgumentParser(
        description="Scaffold PRD directory from codebase analysis"
    )
    parser.add_argument("analysis", help="Path to analysis JSON from codebase_analyzer.py")
    parser.add_argument("-o", "--output-dir", default="prd", help="Output directory (default: prd/)")
    parser.add_argument("-n", "--project-name", help="Override project name")
    parser.add_argument("--validate-only", action="store_true",
                        help="Validate analysis JSON without generating files")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be created without writing files")
    args = parser.parse_args()

    analysis_path = Path(args.analysis)
    if not analysis_path.exists():
        print(f"Error: Analysis file not found: {analysis_path}")
        raise SystemExit(2)

    try:
        with open(analysis_path) as f:
            analysis = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {analysis_path}: {e}")
        raise SystemExit(2)

    # Validate
    errors = validate_analysis(analysis)
    if errors:
        print(f"Validation errors in {analysis_path}:")
        for err in errors:
            print(f"  - {err}")
        raise SystemExit(1)

    if args.validate_only:
        print(f"Analysis file is valid: {analysis_path}")
        routes = analysis.get("routes", {}).get("pages", [])
        print(f"  {len(routes)} routes, "
              f"{len(analysis.get('apis', {}).get('endpoints', []))} APIs, "
              f"{len(analysis.get('enums', {}).get('definitions', []))} enums")
        return

    output_dir = Path(args.output_dir)

    if args.dry_run:
        routes = analysis.get("routes", {}).get("pages", [])
        print(f"Dry run — would create in {output_dir}/:\n")
        print(f"  {output_dir}/README.md")
        for i, route in enumerate(routes, 1):
            name = route_to_page_name(route.get("path", "/"))
            slug = slugify(name) or f"page-{i}"
            print(f"  {output_dir}/pages/{i:02d}-{slug}.md")
        print(f"  {output_dir}/appendix/enum-dictionary.md")
        print(f"  {output_dir}/appendix/api-inventory.md")
        print(f"  {output_dir}/appendix/page-relationships.md")
        print(f"\n  Total: {len(routes) + 4} files")
        return

    print(f"Scaffolding PRD in {output_dir}/...\n")
    scaffold(analysis, output_dir, args.project_name)
    print_summary(output_dir, analysis)
