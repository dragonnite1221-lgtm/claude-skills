# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from migration_generator_base import *  # noqa: F403,E402
# fmt: off
from migration_generator_p1 import Migration, parse_change  # noqa: E402,E501
from migration_generator_p2 import GENERATORS, wrap_prisma, wrap_sql  # noqa: E402,E501
# fmt: on


def wrap_alembic(up: str, down: str, description: str) -> Tuple[str, str]:
    """Format as Alembic Python migration."""
    slug = re.sub(r'\W+', '_', description.lower())[:40]
    revision = datetime.now().strftime("%Y%m%d%H%M")
    template = textwrap.dedent(f'''\
        """
        {description}

        Revision ID: {revision}
        """
        from alembic import op
        import sqlalchemy as sa

        revision = '{revision}'
        down_revision = None  # Set to previous revision


        def upgrade():
            op.execute("""
        {textwrap.indent(up, "        ")}
            """)


        def downgrade():
            op.execute("""
        {textwrap.indent(down, "        ")}
            """)
    ''')
    return template, ""
FORMATTERS = {
    "sql": wrap_sql,
    "prisma": wrap_prisma,
    "alembic": wrap_alembic,
}
def main():
    parser = argparse.ArgumentParser(
        description="Generate database migration templates from change descriptions.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Supported change descriptions:
  "add email_verified boolean to users"
  "drop column legacy_flag from accounts"
  "rename column name to full_name in customers"
  "create table reviews with id, user_id, rating int, body text"
  "drop table temp_imports"
  "add index on orders(status, created_at)"
  "add unique index on users(email)"
  "change email type to varchar in users"

Examples:
  %(prog)s --change "add phone varchar to users" --dialect postgres
  %(prog)s --change "create table reviews with id, user_id, rating int, body" --format prisma
  %(prog)s --change "add index on orders(status)" --output migrations/001.sql --json
        """,
    )
    parser.add_argument("--change", required=True, help="Natural-language description of the schema change")
    parser.add_argument("--dialect", choices=["postgres", "mysql", "sqlite", "sqlserver"],
                        default="postgres", help="Target database dialect (default: postgres)")
    parser.add_argument("--format", choices=["sql", "prisma", "alembic"], default="sql",
                        dest="fmt", help="Output format (default: sql)")
    parser.add_argument("--output", help="Write migration to file instead of stdout")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output as JSON")
    args = parser.parse_args()

    change = parse_change(args.change)
    if not change:
        print(f"Error: Could not parse change description: '{args.change}'", file=sys.stderr)
        print("Run with --help to see supported patterns.", file=sys.stderr)
        sys.exit(1)

    gen_fn = GENERATORS.get(change["op"])
    if not gen_fn:
        print(f"Error: No generator for operation '{change['op']}'", file=sys.stderr)
        sys.exit(1)

    up, down, warnings = gen_fn(change, args.dialect)

    fmt_fn = FORMATTERS[args.fmt]
    up_formatted, down_formatted = fmt_fn(up, down, args.change)

    migration = Migration(
        description=args.change,
        dialect=args.dialect,
        format=args.fmt,
        up=up_formatted,
        down=down_formatted,
        warnings=warnings,
    )

    if args.json_output:
        print(json.dumps(migration.to_dict(), indent=2))
    else:
        if args.output:
            with open(args.output, "w") as f:
                f.write(migration.up)
            print(f"Migration written to {args.output}")
            if migration.down:
                down_path = args.output.replace(".sql", "_down.sql")
                with open(down_path, "w") as f:
                    f.write(migration.down)
                print(f"Rollback written to {down_path}")
        else:
            print(migration.up)
            if migration.down:
                print("\n" + "=" * 40 + " ROLLBACK " + "=" * 40 + "\n")
                print(migration.down)

        if warnings:
            print("\nWarnings:")
            for w in warnings:
                print(f"  - {w}")
