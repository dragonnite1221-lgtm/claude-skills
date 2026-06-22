# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from snowflake_query_helper_base import *  # noqa: F403,E402
# fmt: off
from snowflake_query_helper_p1 import generate_dynamic_table, generate_grants, generate_merge  # noqa: E402,E501
# fmt: on


def main():
    parser = argparse.ArgumentParser(
        description="Generate common Snowflake SQL patterns",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              %(prog)s merge --target customers --source stg --key id --columns name,email
              %(prog)s dynamic-table --name clean_events --warehouse wh --lag "5 min"
              %(prog)s grant --role analyst --database db --schemas public --privileges SELECT
        """),
    )
    parser.add_argument(
        "--json", action="store_true", help="Output as JSON instead of raw SQL"
    )

    subparsers = parser.add_subparsers(dest="command", help="SQL pattern to generate")

    # MERGE subcommand
    merge_p = subparsers.add_parser("merge", help="Generate MERGE (upsert) statement")
    merge_p.add_argument("--target", required=True, help="Target table name")
    merge_p.add_argument("--source", required=True, help="Source table name")
    merge_p.add_argument("--key", required=True, help="Join key column")
    merge_p.add_argument(
        "--columns", required=True, help="Comma-separated columns to merge"
    )
    merge_p.add_argument("--schema", help="Schema prefix (e.g., my_db.my_schema)")

    # Dynamic Table subcommand
    dt_p = subparsers.add_parser(
        "dynamic-table", help="Generate Dynamic Table DDL"
    )
    dt_p.add_argument("--name", required=True, help="Dynamic Table name")
    dt_p.add_argument("--warehouse", required=True, help="Warehouse for refresh")
    dt_p.add_argument(
        "--lag", required=True, help="Target lag (e.g., '5 minutes', '1 hour')"
    )
    dt_p.add_argument("--source", help="Source table name")
    dt_p.add_argument("--columns", help="Comma-separated column list")
    dt_p.add_argument("--schema", help="Schema prefix")

    # Grant subcommand
    grant_p = subparsers.add_parser("grant", help="Generate RBAC grant statements")
    grant_p.add_argument("--role", required=True, help="Role to grant to")
    grant_p.add_argument("--database", required=True, help="Database name")
    grant_p.add_argument(
        "--schemas", required=True, help="Comma-separated schema names"
    )
    grant_p.add_argument(
        "--privileges",
        required=True,
        help="Comma-separated privileges (SELECT, INSERT, UPDATE, DELETE, CREATE TABLE, etc.)",
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "merge":
        cols = [c.strip() for c in args.columns.split(",")]
        sql = generate_merge(args.target, args.source, args.key, cols, args.schema)
    elif args.command == "dynamic-table":
        cols = [c.strip() for c in args.columns.split(",")] if args.columns else None
        sql = generate_dynamic_table(
            args.name, args.warehouse, args.lag, args.source, cols, args.schema
        )
    elif args.command == "grant":
        schemas = [s.strip() for s in args.schemas.split(",")]
        privs = [p.strip() for p in args.privileges.split(",")]
        sql = generate_grants(args.role, args.database, schemas, privs)
    else:
        parser.print_help()
        sys.exit(1)

    if args.json:
        output = {"command": args.command, "sql": sql}
        print(json.dumps(output, indent=2))
    else:
        print(sql)
