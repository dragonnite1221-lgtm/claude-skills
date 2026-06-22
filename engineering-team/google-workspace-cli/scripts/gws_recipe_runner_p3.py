# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from gws_recipe_runner_base import *  # noqa: F403,E402
# fmt: off
from gws_recipe_runner_p2 import RECIPES  # noqa: E402,E501
# fmt: on


PERSONAS: Dict[str, Dict] = {
    "executive-assistant": {
        "description": "Executive assistant managing schedules, emails, and communications",
        "recipes": ["morning-briefing", "today-schedule", "find-time", "send-email", "reply-to-thread",
                     "standup-report", "meeting-prep", "eod-wrap", "quick-event", "inbox-zero"],
    },
    "pm": {
        "description": "Project manager tracking tasks, meetings, and deliverables",
        "recipes": ["standup-report", "create-event", "find-time", "task-create", "task-progress",
                     "project-status", "weekly-summary", "share-folder", "sheet-read", "morning-briefing"],
    },
    "hr": {
        "description": "HR managing people, onboarding, and communications",
        "recipes": ["list-users", "user-info", "send-email", "create-event", "create-doc",
                     "share-folder", "chat-message", "list-groups", "export-contacts", "today-schedule"],
    },
    "sales": {
        "description": "Sales rep managing client communications and proposals",
        "recipes": ["send-email", "search-emails", "create-event", "find-time", "create-doc",
                     "share-file", "sheet-read", "sheet-write", "export-file", "morning-briefing"],
    },
    "it-admin": {
        "description": "IT administrator managing Workspace configuration and security",
        "recipes": ["list-users", "list-groups", "user-info", "audit-logins", "drive-activity",
                     "find-large-files", "cleanup-trash", "label-manager", "filter-setup", "share-folder"],
    },
    "developer": {
        "description": "Developer using Workspace APIs for automation",
        "recipes": ["sheet-read", "sheet-write", "sheet-append", "upload-file", "create-doc",
                     "chat-message", "task-create", "list-files", "export-file", "send-email"],
    },
    "marketing": {
        "description": "Marketing team member managing campaigns and content",
        "recipes": ["send-email", "create-doc", "share-file", "upload-file", "create-sheet",
                     "sheet-write", "chat-message", "create-event", "email-stats", "weekly-summary"],
    },
    "finance": {
        "description": "Finance team managing spreadsheets and reports",
        "recipes": ["sheet-read", "sheet-write", "sheet-append", "create-sheet", "export-file",
                     "share-file", "send-email", "find-large-files", "drive-activity", "weekly-summary"],
    },
    "legal": {
        "description": "Legal team managing documents and compliance",
        "recipes": ["create-doc", "share-file", "export-file", "search-emails", "send-email",
                     "upload-file", "list-files", "drive-activity", "audit-logins", "find-large-files"],
    },
    "support": {
        "description": "Customer support managing tickets and communications",
        "recipes": ["search-emails", "send-email", "reply-to-thread", "label-manager", "filter-setup",
                     "task-create", "chat-message", "unread-digest", "inbox-zero", "morning-briefing"],
    },
}
def list_recipes(persona: Optional[str], output_json: bool):
    """List all recipes, optionally filtered by persona."""
    if persona:
        if persona not in PERSONAS:
            print(f"Unknown persona: {persona}. Available: {', '.join(PERSONAS.keys())}")
            sys.exit(1)
        recipe_names = PERSONAS[persona]["recipes"]
        recipes = {k: v for k, v in RECIPES.items() if k in recipe_names}
        title = f"Recipes for {persona.upper()}: {PERSONAS[persona]['description']}"
    else:
        recipes = RECIPES
        title = "All 43 Google Workspace CLI Recipes"

    if output_json:
        output = []
        for name, r in recipes.items():
            output.append(asdict(r))
        print(json.dumps(output, indent=2))
        return

    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

    by_category: Dict[str, list] = {}
    for name, r in recipes.items():
        by_category.setdefault(r.category, []).append(r)

    for cat, cat_recipes in sorted(by_category.items()):
        print(f"  {cat.upper()} ({len(cat_recipes)})")
        for r in cat_recipes:
            svcs = ",".join(r.services)
            print(f"    {r.name:<24} {r.description:<40} [{svcs}]")
        print()

    print(f"  Total: {len(recipes)} recipes")
    print(f"\n{'='*60}\n")
def search_recipes(keyword: str, output_json: bool):
    """Search recipes by keyword."""
    keyword_lower = keyword.lower()
    matches = {k: v for k, v in RECIPES.items()
               if keyword_lower in k.lower()
               or keyword_lower in v.description.lower()
               or keyword_lower in v.category.lower()
               or any(keyword_lower in s for s in v.services)}

    if output_json:
        print(json.dumps([asdict(r) for r in matches.values()], indent=2))
        return

    print(f"\n  Search results for '{keyword}': {len(matches)} matches\n")
    for name, r in matches.items():
        print(f"    {r.name:<24} {r.description}")
    print()
def describe_recipe(name: str, output_json: bool):
    """Show full details for a recipe."""
    recipe = RECIPES.get(name)
    if not recipe:
        print(f"Unknown recipe: {name}")
        print(f"Use --list to see available recipes")
        sys.exit(1)

    if output_json:
        print(json.dumps(asdict(recipe), indent=2))
        return

    print(f"\n{'='*60}")
    print(f"  Recipe: {recipe.name}")
    print(f"{'='*60}\n")
    print(f"  Description: {recipe.description}")
    print(f"  Category:    {recipe.category}")
    print(f"  Services:    {', '.join(recipe.services)}")
    if recipe.prerequisites:
        print(f"  Prerequisites: {recipe.prerequisites}")
    print(f"\n  Commands:")
    for i, cmd in enumerate(recipe.commands, 1):
        print(f"    {i}. {cmd}")
    print(f"\n{'='*60}\n")
