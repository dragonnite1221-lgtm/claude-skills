# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from migration_generator_base import *  # noqa: F403,E402
# fmt: off
from migration_generator_p1 import gen_add_column, gen_drop_column, map_type  # noqa: E402,E501
# fmt: on


def gen_rename_column(change: dict, dialect: str) -> Tuple[str, str, List[str]]:
    table = change["table"]
    old, new = change["old"], change["new"]
    warnings = []
    if dialect == "postgres":
        up = f"ALTER TABLE {table} RENAME COLUMN {old} TO {new};"
        down = f"ALTER TABLE {table} RENAME COLUMN {new} TO {old};"
    elif dialect == "mysql":
        up = f"ALTER TABLE {table} RENAME COLUMN {old} TO {new};"
        down = f"ALTER TABLE {table} RENAME COLUMN {new} TO {old};"
    elif dialect == "sqlite":
        up = f"ALTER TABLE {table} RENAME COLUMN {old} TO {new};"
        down = f"ALTER TABLE {table} RENAME COLUMN {new} TO {old};"
        warnings.append("SQLite RENAME COLUMN requires version 3.25.0+.")
    elif dialect == "sqlserver":
        up = f"EXEC sp_rename '{table}.{old}', '{new}', 'COLUMN';"
        down = f"EXEC sp_rename '{table}.{new}', '{old}', 'COLUMN';"
    else:
        up = f"ALTER TABLE {table} RENAME COLUMN {old} TO {new};"
        down = f"ALTER TABLE {table} RENAME COLUMN {new} TO {old};"
    return up, down, warnings
def gen_add_table(change: dict, dialect: str) -> Tuple[str, str, List[str]]:
    table = change["table"]
    cols = change["columns"]
    col_defs = []
    has_id = False
    for col in cols:
        col = col.strip()
        if col.lower() == "id":
            has_id = True
            if dialect == "postgres":
                col_defs.append("    id SERIAL PRIMARY KEY")
            elif dialect == "mysql":
                col_defs.append("    id INT AUTO_INCREMENT PRIMARY KEY")
            elif dialect == "sqlite":
                col_defs.append("    id INTEGER PRIMARY KEY AUTOINCREMENT")
            elif dialect == "sqlserver":
                col_defs.append("    id INT IDENTITY(1,1) PRIMARY KEY")
        else:
            # Check if type is specified (e.g., "rating int")
            parts = col.split()
            if len(parts) >= 2:
                col_defs.append(f"    {parts[0]} {map_type(parts[1], dialect)}")
            else:
                col_defs.append(f"    {col} TEXT")

    cols_sql = ",\n".join(col_defs)
    up = f"CREATE TABLE {table} (\n{cols_sql}\n);"
    down = f"DROP TABLE {table};"
    warnings = []
    if not has_id:
        warnings.append("Table has no explicit primary key. Consider adding an 'id' column.")
    return up, down, warnings
def gen_drop_table(change: dict, dialect: str) -> Tuple[str, str, List[str]]:
    table = change["table"]
    up = f"DROP TABLE {table};"
    down = f"-- WARNING: Cannot reverse DROP TABLE without original DDL.\nCREATE TABLE {table} (id INTEGER PRIMARY KEY);"
    return up, down, ["Down migration is a placeholder. Replace with the original CREATE TABLE statement."]
def gen_add_index(change: dict, dialect: str) -> Tuple[str, str, List[str]]:
    table = change["table"]
    cols = change["columns"]
    unique = "UNIQUE " if change.get("unique") else ""
    idx_name = f"idx_{table}_{'_'.join(cols)}"
    if dialect == "postgres":
        up = f"CREATE {unique}INDEX CONCURRENTLY {idx_name} ON {table} ({', '.join(cols)});"
    else:
        up = f"CREATE {unique}INDEX {idx_name} ON {table} ({', '.join(cols)});"
    down = f"DROP INDEX {idx_name};" if dialect != "mysql" else f"DROP INDEX {idx_name} ON {table};"
    warnings = []
    if dialect == "postgres":
        warnings.append("CONCURRENTLY cannot run inside a transaction. Run outside migration transaction.")
    return up, down, warnings
def gen_change_type(change: dict, dialect: str) -> Tuple[str, str, List[str]]:
    table = change["table"]
    col = change["column"]
    new_type = map_type(change["new_type"], dialect)
    warnings = ["Down migration uses TEXT as placeholder. Replace with the original column type."]
    if dialect == "postgres":
        up = f"ALTER TABLE {table} ALTER COLUMN {col} TYPE {new_type};"
        down = f"ALTER TABLE {table} ALTER COLUMN {col} TYPE TEXT;"
    elif dialect == "mysql":
        up = f"ALTER TABLE {table} MODIFY COLUMN {col} {new_type};"
        down = f"ALTER TABLE {table} MODIFY COLUMN {col} TEXT;"
    elif dialect == "sqlserver":
        up = f"ALTER TABLE {table} ALTER COLUMN {col} {new_type};"
        down = f"ALTER TABLE {table} ALTER COLUMN {col} NVARCHAR(MAX);"
    else:
        up = f"-- SQLite does not support ALTER COLUMN. Recreate the table."
        down = f"-- SQLite does not support ALTER COLUMN. Recreate the table."
        warnings.append("SQLite requires table recreation for type changes.")
    return up, down, warnings
GENERATORS = {
    "add_column": gen_add_column,
    "drop_column": gen_drop_column,
    "rename_column": gen_rename_column,
    "add_table": gen_add_table,
    "drop_table": gen_drop_table,
    "add_index": gen_add_index,
    "change_type": gen_change_type,
}
def wrap_sql(up: str, down: str, description: str) -> Tuple[str, str]:
    """Wrap as plain SQL migration files."""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    header = f"-- Migration: {description}\n-- Generated: {datetime.now().isoformat()}\n\n"
    return header + "-- Up\n" + up, header + "-- Down\n" + down
def wrap_prisma(up: str, down: str, description: str) -> Tuple[str, str]:
    """Format as Prisma migration SQL (Prisma uses raw SQL in migration.sql)."""
    header = f"-- Migration: {description}\n-- Format: Prisma (migration.sql)\n\n"
    return header + up, header + "-- Rollback\n" + down
