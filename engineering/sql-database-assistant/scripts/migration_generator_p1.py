# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from migration_generator_base import *  # noqa: F403,E402


@dataclass
class Migration:
    """A generated migration with up and down scripts."""
    description: str
    dialect: str
    format: str
    up: str
    down: str
    warnings: List[str]

    def to_dict(self):
        return asdict(self)
def parse_add_column(desc: str) -> Optional[dict]:
    """Parse: add <column> <type> to <table>"""
    m = re.match(
        r'add\s+(?:column\s+)?(\w+)\s+(\w[\w(),.]*)\s+(?:to|on)\s+(\w+)',
        desc, re.IGNORECASE,
    )
    if m:
        return {"op": "add_column", "column": m.group(1), "type": m.group(2), "table": m.group(3)}
    return None
def parse_drop_column(desc: str) -> Optional[dict]:
    """Parse: drop/remove <column> from <table>"""
    m = re.match(
        r'(?:drop|remove)\s+(?:column\s+)?(\w+)\s+from\s+(\w+)',
        desc, re.IGNORECASE,
    )
    if m:
        return {"op": "drop_column", "column": m.group(1), "table": m.group(2)}
    return None
def parse_rename_column(desc: str) -> Optional[dict]:
    """Parse: rename column <old> to <new> in <table>"""
    m = re.match(
        r'rename\s+column\s+(\w+)\s+to\s+(\w+)\s+in\s+(\w+)',
        desc, re.IGNORECASE,
    )
    if m:
        return {"op": "rename_column", "old": m.group(1), "new": m.group(2), "table": m.group(3)}
    return None
def parse_add_table(desc: str) -> Optional[dict]:
    """Parse: create table <name> with <col1>, <col2>, ..."""
    m = re.match(
        r'create\s+table\s+(\w+)\s+with\s+(.+)',
        desc, re.IGNORECASE,
    )
    if m:
        cols = [c.strip() for c in m.group(2).split(",")]
        return {"op": "add_table", "table": m.group(1), "columns": cols}
    return None
def parse_drop_table(desc: str) -> Optional[dict]:
    """Parse: drop table <name>"""
    m = re.match(r'drop\s+table\s+(\w+)', desc, re.IGNORECASE)
    if m:
        return {"op": "drop_table", "table": m.group(1)}
    return None
def parse_add_index(desc: str) -> Optional[dict]:
    """Parse: add index on <table>(<col1>, <col2>)"""
    m = re.match(
        r'add\s+(?:unique\s+)?index\s+(?:on\s+)?(\w+)\s*\(([^)]+)\)',
        desc, re.IGNORECASE,
    )
    if m:
        unique = "unique" in desc.lower()
        cols = [c.strip() for c in m.group(2).split(",")]
        return {"op": "add_index", "table": m.group(1), "columns": cols, "unique": unique}
    return None
def parse_change_type(desc: str) -> Optional[dict]:
    """Parse: change <column> type to <type> in <table>"""
    m = re.match(
        r'change\s+(?:column\s+)?(\w+)\s+type\s+to\s+(\w[\w(),.]*)\s+in\s+(\w+)',
        desc, re.IGNORECASE,
    )
    if m:
        return {"op": "change_type", "column": m.group(1), "new_type": m.group(2), "table": m.group(3)}
    return None
PARSERS = [
    parse_add_column,
    parse_drop_column,
    parse_rename_column,
    parse_add_table,
    parse_drop_table,
    parse_add_index,
    parse_change_type,
]
def parse_change(desc: str) -> Optional[dict]:
    for parser in PARSERS:
        result = parser(desc)
        if result:
            return result
    return None
TYPE_MAP = {
    "boolean": {"postgres": "BOOLEAN", "mysql": "TINYINT(1)", "sqlite": "INTEGER", "sqlserver": "BIT"},
    "text": {"postgres": "TEXT", "mysql": "TEXT", "sqlite": "TEXT", "sqlserver": "NVARCHAR(MAX)"},
    "integer": {"postgres": "INTEGER", "mysql": "INT", "sqlite": "INTEGER", "sqlserver": "INT"},
    "int": {"postgres": "INTEGER", "mysql": "INT", "sqlite": "INTEGER", "sqlserver": "INT"},
    "serial": {"postgres": "SERIAL", "mysql": "INT AUTO_INCREMENT", "sqlite": "INTEGER", "sqlserver": "INT IDENTITY(1,1)"},
    "varchar": {"postgres": "VARCHAR(255)", "mysql": "VARCHAR(255)", "sqlite": "TEXT", "sqlserver": "NVARCHAR(255)"},
    "timestamp": {"postgres": "TIMESTAMP", "mysql": "DATETIME", "sqlite": "TEXT", "sqlserver": "DATETIME2"},
    "uuid": {"postgres": "UUID", "mysql": "CHAR(36)", "sqlite": "TEXT", "sqlserver": "UNIQUEIDENTIFIER"},
    "json": {"postgres": "JSONB", "mysql": "JSON", "sqlite": "TEXT", "sqlserver": "NVARCHAR(MAX)"},
    "decimal": {"postgres": "DECIMAL(19,4)", "mysql": "DECIMAL(19,4)", "sqlite": "REAL", "sqlserver": "DECIMAL(19,4)"},
    "float": {"postgres": "DOUBLE PRECISION", "mysql": "DOUBLE", "sqlite": "REAL", "sqlserver": "FLOAT"},
}
def map_type(type_name: str, dialect: str) -> str:
    """Map a generic type name to a dialect-specific type."""
    key = type_name.lower().rstrip("()")
    if key in TYPE_MAP and dialect in TYPE_MAP[key]:
        return TYPE_MAP[key][dialect]
    return type_name.upper()
def gen_add_column(change: dict, dialect: str) -> Tuple[str, str, List[str]]:
    col_type = map_type(change["type"], dialect)
    table = change["table"]
    col = change["column"]
    up = f"ALTER TABLE {table} ADD COLUMN {col} {col_type};"
    down = f"ALTER TABLE {table} DROP COLUMN {col};"
    return up, down, []
def gen_drop_column(change: dict, dialect: str) -> Tuple[str, str, List[str]]:
    table = change["table"]
    col = change["column"]
    up = f"ALTER TABLE {table} DROP COLUMN {col};"
    down = f"-- WARNING: Cannot fully reverse DROP COLUMN. Provide the original type.\nALTER TABLE {table} ADD COLUMN {col} TEXT;"
    return up, down, ["Down migration uses TEXT as placeholder. Replace with the original column type."]
