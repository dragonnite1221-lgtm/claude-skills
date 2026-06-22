# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from snowflake_query_helper_base import *  # noqa: F403,E402


def generate_merge(
    target: str,
    source: str,
    key: str,
    columns: List[str],
    schema: Optional[str] = None,
) -> str:
    """Generate a MERGE (upsert) statement following Snowflake best practices."""
    prefix = f"{schema}." if schema else ""
    t = f"{prefix}{target}"
    s = f"{prefix}{source}"

    # Filter out updated_at from user columns to avoid duplicates
    merge_cols = [col for col in columns if col != "updated_at"]

    update_sets = ",\n        ".join(
        f"t.{col} = s.{col}" for col in merge_cols
    )
    update_sets += ",\n        t.updated_at = CURRENT_TIMESTAMP()"

    insert_cols = ", ".join([key] + merge_cols + ["updated_at"])
    insert_vals = ", ".join(
        [f"s.{key}"] + [f"s.{col}" for col in merge_cols] + ["CURRENT_TIMESTAMP()"]
    )

    return textwrap.dedent(f"""\
        MERGE INTO {t} t
        USING {s} s
            ON t.{key} = s.{key}
        WHEN MATCHED THEN
            UPDATE SET
                {update_sets}
        WHEN NOT MATCHED THEN
            INSERT ({insert_cols})
            VALUES ({insert_vals});""")
def generate_dynamic_table(
    name: str,
    warehouse: str,
    lag: str,
    source: Optional[str] = None,
    columns: Optional[List[str]] = None,
    schema: Optional[str] = None,
) -> str:
    """Generate a Dynamic Table DDL with best-practice defaults."""
    prefix = f"{schema}." if schema else ""
    full_name = f"{prefix}{name}"
    src = source or "<source_table>"
    col_list = ", ".join(columns) if columns else "<col1>, <col2>, <col3>"

    return textwrap.dedent(f"""\
        CREATE OR REPLACE DYNAMIC TABLE {full_name}
            TARGET_LAG = '{lag}'
            WAREHOUSE = {warehouse}
            AS
            SELECT {col_list}
            FROM {src}
            WHERE 1=1;  -- Add your filter conditions

        -- Verify refresh mode (incremental is preferred):
        -- SELECT name, refresh_mode, refresh_mode_reason
        -- FROM TABLE(INFORMATION_SCHEMA.DYNAMIC_TABLES())
        -- WHERE name = '{name.upper()}';""")
def generate_grants(
    role: str,
    database: str,
    schemas: List[str],
    privileges: List[str],
) -> str:
    """Generate RBAC grant statements following least-privilege principles."""
    lines = [f"-- RBAC grants for role: {role}"]
    lines.append(f"-- Generated following least-privilege principles")
    lines.append("")

    # Database-level
    lines.append(f"GRANT USAGE ON DATABASE {database} TO ROLE {role};")
    lines.append("")

    for schema in schemas:
        fq_schema = f"{database}.{schema}"
        lines.append(f"-- Schema: {fq_schema}")
        lines.append(f"GRANT USAGE ON SCHEMA {fq_schema} TO ROLE {role};")

        for priv in privileges:
            p = priv.strip().upper()
            if p == "USAGE":
                continue  # Already granted above
            elif p == "SELECT":
                lines.append(
                    f"GRANT SELECT ON ALL TABLES IN SCHEMA {fq_schema} TO ROLE {role};"
                )
                lines.append(
                    f"GRANT SELECT ON FUTURE TABLES IN SCHEMA {fq_schema} TO ROLE {role};"
                )
                lines.append(
                    f"GRANT SELECT ON ALL VIEWS IN SCHEMA {fq_schema} TO ROLE {role};"
                )
                lines.append(
                    f"GRANT SELECT ON FUTURE VIEWS IN SCHEMA {fq_schema} TO ROLE {role};"
                )
            elif p in ("INSERT", "UPDATE", "DELETE", "TRUNCATE"):
                lines.append(
                    f"GRANT {p} ON ALL TABLES IN SCHEMA {fq_schema} TO ROLE {role};"
                )
                lines.append(
                    f"GRANT {p} ON FUTURE TABLES IN SCHEMA {fq_schema} TO ROLE {role};"
                )
            elif p == "CREATE TABLE":
                lines.append(
                    f"GRANT CREATE TABLE ON SCHEMA {fq_schema} TO ROLE {role};"
                )
            elif p == "CREATE VIEW":
                lines.append(
                    f"GRANT CREATE VIEW ON SCHEMA {fq_schema} TO ROLE {role};"
                )
            else:
                lines.append(
                    f"GRANT {p} ON SCHEMA {fq_schema} TO ROLE {role};"
                )
        lines.append("")

    return "\n".join(lines)
