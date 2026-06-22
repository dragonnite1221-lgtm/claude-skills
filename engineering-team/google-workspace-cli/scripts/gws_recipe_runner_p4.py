# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from gws_recipe_runner_base import *  # noqa: F403,E402
# fmt: off
from gws_recipe_runner_p2 import RECIPES  # noqa: E402,E501
from gws_recipe_runner_p3 import PERSONAS, describe_recipe, list_recipes, search_recipes  # noqa: E402,E501
# fmt: on


def run_recipe(name: str, dry_run: bool):
    """Execute a recipe (or print commands in dry-run mode)."""
    recipe = RECIPES.get(name)
    if not recipe:
        print(f"Unknown recipe: {name}")
        sys.exit(1)

    if dry_run:
        print(f"\n  [DRY RUN] Recipe: {recipe.name}\n")
        for i, cmd in enumerate(recipe.commands, 1):
            print(f"  {i}. {cmd}")
        print(f"\n  (No commands executed)")
        return

    print(f"\n  Executing recipe: {recipe.name}\n")
    for cmd in recipe.commands:
        if cmd.startswith("#"):
            print(f"  {cmd}")
            continue
        print(f"  $ {cmd}")
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            if result.stdout:
                print(result.stdout)
            if result.returncode != 0 and result.stderr:
                print(f"  Error: {result.stderr.strip()[:200]}")
        except subprocess.TimeoutExpired:
            print(f"  Timeout after 30s")
        except OSError as e:
            print(f"  Execution error: {e}")
def list_personas(output_json: bool):
    """List all available personas."""
    if output_json:
        print(json.dumps(PERSONAS, indent=2))
        return

    print(f"\n{'='*60}")
    print(f"  10 PERSONA BUNDLES")
    print(f"{'='*60}\n")
    for name, p in PERSONAS.items():
        print(f"  {name:<24} {p['description']}")
        print(f"  {'':24} Recipes: {', '.join(p['recipes'][:5])}...")
        print()
    print(f"{'='*60}\n")
def main():
    parser = argparse.ArgumentParser(
        description="Catalog, search, and execute Google Workspace CLI recipes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --list                           # List all 43 recipes
  %(prog)s --list --persona pm              # Recipes for project managers
  %(prog)s --search "email"                 # Search by keyword
  %(prog)s --describe standup-report        # Full recipe details
  %(prog)s --run standup-report --dry-run   # Preview recipe commands
  %(prog)s --personas                       # List all 10 personas
  %(prog)s --list --json                    # JSON output
        """,
    )
    parser.add_argument("--list", action="store_true", help="List all recipes")
    parser.add_argument("--search", help="Search recipes by keyword")
    parser.add_argument("--describe", help="Show full details for a recipe")
    parser.add_argument("--run", help="Execute a recipe")
    parser.add_argument("--dry-run", action="store_true", help="Print commands without executing")
    parser.add_argument("--persona", help="Filter recipes by persona")
    parser.add_argument("--personas", action="store_true", help="List all personas")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    if not any([args.list, args.search, args.describe, args.run, args.personas]):
        parser.print_help()
        return

    if args.personas:
        list_personas(args.json)
        return

    if args.list:
        list_recipes(args.persona, args.json)
        return

    if args.search:
        search_recipes(args.search, args.json)
        return

    if args.describe:
        describe_recipe(args.describe, args.json)
        return

    if args.run:
        run_recipe(args.run, args.dry_run)
        return
