# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from schema_explorer_base import *  # noqa: F403,E402
# fmt: off
from schema_explorer_p2 import generate_json_output, generate_md  # noqa: E402,E501
# fmt: on


def main():
    parser = argparse.ArgumentParser(
        description="Generate schema documentation from database introspection.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --dialect postgres --tables all --format md
  %(prog)s --dialect mysql --tables users,orders --format json
  %(prog)s --dialect sqlite --tables all --json
        """,
    )
    parser.add_argument(
        "--dialect", required=True, choices=["postgres", "mysql", "sqlite", "sqlserver"],
        help="Target database dialect",
    )
    parser.add_argument(
        "--tables", default="all",
        help="Comma-separated table names or 'all' (default: all)",
    )
    parser.add_argument(
        "--format", choices=["md", "json"], default="md", dest="fmt",
        help="Output format (default: md)",
    )
    parser.add_argument(
        "--json", action="store_true", dest="json_output",
        help="Output as JSON (overrides --format)",
    )
    args = parser.parse_args()

    tables = [t.strip() for t in args.tables.split(",")]

    if args.json_output or args.fmt == "json":
        result = generate_json_output(args.dialect, tables)
        print(json.dumps(result, indent=2))
    else:
        print(generate_md(args.dialect, tables))
