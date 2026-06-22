# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from frontend_scaffolder_base import *  # noqa: F403,E402
# fmt: off
from frontend_scaffolder_p1 import TEMPLATES  # noqa: E402,E501
from frontend_scaffolder_p2 import FEATURES  # noqa: E402,E501
from frontend_scaffolder_p9 import print_result, scaffold_project  # noqa: E402,E501
# fmt: on


def main():
    parser = argparse.ArgumentParser(
        description="Scaffold a frontend project with best practices"
    )
    parser.add_argument(
        "name",
        help="Project name (kebab-case recommended)"
    )
    parser.add_argument(
        "--dir", "-d",
        default=".",
        help="Output directory (default: current directory)"
    )
    parser.add_argument(
        "--template", "-t",
        choices=list(TEMPLATES.keys()),
        default="nextjs",
        help="Project template (default: nextjs)"
    )
    parser.add_argument(
        "--features", "-f",
        help="Comma-separated features to add (auth,api,forms,testing,storybook)"
    )
    parser.add_argument(
        "--list-templates",
        action="store_true",
        help="List available templates"
    )
    parser.add_argument(
        "--list-features",
        action="store_true",
        help="List available features"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be created without creating files"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format"
    )

    args = parser.parse_args()

    if args.list_templates:
        print("\nAvailable Templates:")
        for key, template in TEMPLATES.items():
            print(f"  {key}: {template['name']}")
            print(f"    {template['description']}")
        return

    if args.list_features:
        print("\nAvailable Features:")
        for key, feature in FEATURES.items():
            print(f"  {key}: {feature['description']}")
            deps = ", ".join(feature.get("dependencies", []))
            if deps:
                print(f"    Adds: {deps}")
        return

    features = []
    if args.features:
        features = [f.strip() for f in args.features.split(",")]
        invalid = [f for f in features if f not in FEATURES]
        if invalid:
            print(f"Unknown features: {', '.join(invalid)}", file=sys.stderr)
            print(f"Valid features: {', '.join(FEATURES.keys())}")
            sys.exit(1)

    result = scaffold_project(
        name=args.name,
        output_dir=Path(args.dir),
        template=args.template,
        features=features,
        dry_run=args.dry_run,
    )

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_result(result)
