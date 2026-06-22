# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from spec_generator_base import *  # noqa: F403,E402
# fmt: off
from spec_generator_p2 import generate_spec, generate_spec_json  # noqa: E402,E501
# fmt: on


def main():
    parser = argparse.ArgumentParser(
        description="Generate a feature specification template from a name and description.",
        epilog="Example: python spec_generator.py --name 'User Auth' --description 'OAuth 2.0 login flow'",
    )
    parser.add_argument(
        "--name",
        required=True,
        help="Feature name (used as spec title)",
    )
    parser.add_argument(
        "--description",
        default="",
        help="Brief feature description (used to seed the context section)",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=None,
        help="Output file path (default: stdout)",
    )
    parser.add_argument(
        "--format",
        choices=["md", "json"],
        default="md",
        help="Output format: md (markdown) or json (default: md)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_flag",
        help="Shorthand for --format json",
    )

    args = parser.parse_args()

    output_format = "json" if args.json_flag else args.format

    if output_format == "json":
        result = generate_spec_json(args.name, args.description)
        output = json.dumps(result, indent=2)
    else:
        output = generate_spec(args.name, args.description)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output, encoding="utf-8")
        print(f"Spec template written to {out_path}", file=sys.stderr)
    else:
        print(output)

    sys.exit(0)
