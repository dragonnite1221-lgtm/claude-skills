# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from component_generator_base import *  # noqa: F403,E402
# fmt: off
from component_generator_p1 import to_pascal_case  # noqa: E402,E501
from component_generator_p2 import generate_component, print_result  # noqa: E402,E501
# fmt: on


def main():
    parser = argparse.ArgumentParser(
        description="Generate React/Next.js components with TypeScript and Tailwind CSS"
    )
    parser.add_argument(
        "name",
        help="Component name (PascalCase or kebab-case)"
    )
    parser.add_argument(
        "--dir", "-d",
        default="src/components",
        help="Output directory (default: src/components)"
    )
    parser.add_argument(
        "--type", "-t",
        choices=["client", "server", "hook"],
        default="client",
        help="Component type (default: client)"
    )
    parser.add_argument(
        "--with-test",
        action="store_true",
        help="Generate test file"
    )
    parser.add_argument(
        "--with-story",
        action="store_true",
        help="Generate Storybook story file"
    )
    parser.add_argument(
        "--no-index",
        action="store_true",
        help="Skip generating index.ts file"
    )
    parser.add_argument(
        "--flat",
        action="store_true",
        help="Create files directly in output dir without subdirectory"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be generated without creating files"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )

    args = parser.parse_args()

    output_dir = Path(args.dir)
    pascal_name = to_pascal_case(args.name)

    if args.dry_run:
        print(f"\nDry run - would generate:")
        print(f"  Component: {pascal_name}")
        print(f"  Type: {args.type}")
        print(f"  Directory: {output_dir / pascal_name if not args.flat else output_dir}")
        print(f"  Test: {'Yes' if args.with_test else 'No'}")
        print(f"  Story: {'Yes' if args.with_story else 'No'}")
        return

    try:
        result = generate_component(
            name=args.name,
            output_dir=output_dir,
            component_type=args.type,
            with_test=args.with_test,
            with_story=args.with_story,
            with_index=not args.no_index,
            flat=args.flat,
        )
        print_result(result, args.verbose)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
