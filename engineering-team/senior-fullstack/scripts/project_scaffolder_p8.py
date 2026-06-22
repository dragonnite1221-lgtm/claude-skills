# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from project_scaffolder_base import *  # noqa: F403,E402
# fmt: off
from project_scaffolder_p7 import create_project, list_templates  # noqa: E402,E501
# fmt: on


def print_result(result: Dict, as_json: bool = False) -> None:
    """Print result."""
    if as_json:
        print(json.dumps(result, indent=2))
        return

    if "templates" in result:
        print("\nAvailable Templates:")
        print("=" * 50)
        for t in result["templates"]:
            print(f"\n  {t['name']}")
            print(f"    {t['description']}")
        return

    if not result.get("success"):
        print(f"Error: {result.get('error')}")
        return

    print("\n" + "=" * 50)
    print("Project Created Successfully")
    print("=" * 50)
    print(f"Project: {result['project_name']}")
    print(f"Template: {result['template']}")
    print(f"Location: {result['location']}")
    print(f"Files: {result['files_created']}")
    print("\nNext Steps:")
    for i, step in enumerate(result["next_steps"], 1):
        print(f"  {i}. {step}")
    print()
def main():
    parser = argparse.ArgumentParser(
        description="Generate fullstack project scaffolding",
        epilog="Examples:\n  %(prog)s nextjs my-app\n  %(prog)s fastapi-react my-api\n  %(prog)s --list-templates",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("template", nargs="?", help="Project template")
    parser.add_argument("project_name", nargs="?", help="Project name")
    parser.add_argument("--output", "-o", default=".", help="Output directory")
    parser.add_argument("--list-templates", "-l", action="store_true", help="List templates")
    parser.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()

    if args.list_templates:
        print_result(list_templates(), args.json)
        return

    if not args.template or not args.project_name:
        parser.print_help()
        sys.exit(1)

    result = create_project(args.template, args.project_name, Path(args.output).resolve())
    print_result(result, args.json)

    if not result.get("success"):
        sys.exit(1)
