# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from query_optimizer_base import *  # noqa: F403,E402
# fmt: off
from query_optimizer_p2 import analyze_query, format_json, format_text, split_queries  # noqa: E402,E501
# fmt: on


def main():
    parser = argparse.ArgumentParser(
        description="Analyze SQL queries for common performance issues.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --query "SELECT * FROM users"
  %(prog)s --query queries.sql --dialect mysql
  %(prog)s --query "DELETE FROM orders" --json
        """,
    )
    parser.add_argument(
        "--query", required=True,
        help="SQL query string or path to a .sql file",
    )
    parser.add_argument(
        "--dialect", choices=["postgres", "mysql", "sqlite", "sqlserver"],
        default="postgres", help="SQL dialect (default: postgres)",
    )
    parser.add_argument(
        "--json", action="store_true", dest="json_output",
        help="Output results as JSON",
    )
    args = parser.parse_args()

    # Determine if query is a file path or inline SQL
    sql_text = args.query
    if os.path.isfile(args.query):
        with open(args.query, "r") as f:
            sql_text = f.read()

    queries = split_queries(sql_text)
    if not queries:
        # Treat the whole input as a single query
        queries = [sql_text.strip()]

    analyses = [analyze_query(q, args.dialect) for q in queries]

    if args.json_output:
        print(format_json(analyses))
    else:
        print(format_text(analyses))
