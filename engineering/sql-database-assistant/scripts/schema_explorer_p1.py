# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from schema_explorer_base import *  # noqa: F403,E402


INTROSPECTION_QUERIES: Dict[str, Dict[str, str]] = {
    "postgres": {
        "tables": textwrap.dedent("""\
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            ORDER BY table_name;"""),
        "columns": textwrap.dedent("""\
            SELECT table_name, column_name, data_type, character_maximum_length,
                   is_nullable, column_default
            FROM information_schema.columns
            WHERE table_schema = 'public' {table_filter}
            ORDER BY table_name, ordinal_position;"""),
        "primary_keys": textwrap.dedent("""\
            SELECT tc.table_name, kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
              ON tc.constraint_name = kcu.constraint_name
            WHERE tc.constraint_type = 'PRIMARY KEY' AND tc.table_schema = 'public'
            ORDER BY tc.table_name;"""),
        "foreign_keys": textwrap.dedent("""\
            SELECT tc.table_name, kcu.column_name,
                   ccu.table_name AS foreign_table, ccu.column_name AS foreign_column
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
              ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage ccu
              ON tc.constraint_name = ccu.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
            ORDER BY tc.table_name;"""),
        "indexes": textwrap.dedent("""\
            SELECT schemaname, tablename, indexname, indexdef
            FROM pg_indexes
            WHERE schemaname = 'public'
            ORDER BY tablename, indexname;"""),
        "table_sizes": textwrap.dedent("""\
            SELECT relname AS table_name,
                   pg_size_pretty(pg_total_relation_size(relid)) AS total_size,
                   pg_size_pretty(pg_relation_size(relid)) AS data_size,
                   pg_size_pretty(pg_total_relation_size(relid) - pg_relation_size(relid)) AS index_size
            FROM pg_catalog.pg_statio_user_tables
            ORDER BY pg_total_relation_size(relid) DESC;"""),
    },
    "mysql": {
        "tables": textwrap.dedent("""\
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = DATABASE() AND table_type = 'BASE TABLE'
            ORDER BY table_name;"""),
        "columns": textwrap.dedent("""\
            SELECT table_name, column_name, column_type, is_nullable,
                   column_default, column_key, extra
            FROM information_schema.columns
            WHERE table_schema = DATABASE() {table_filter}
            ORDER BY table_name, ordinal_position;"""),
        "foreign_keys": textwrap.dedent("""\
            SELECT table_name, column_name, referenced_table_name, referenced_column_name
            FROM information_schema.key_column_usage
            WHERE table_schema = DATABASE() AND referenced_table_name IS NOT NULL
            ORDER BY table_name;"""),
        "indexes": textwrap.dedent("""\
            SELECT table_name, index_name, non_unique, column_name, seq_in_index
            FROM information_schema.statistics
            WHERE table_schema = DATABASE()
            ORDER BY table_name, index_name, seq_in_index;"""),
        "table_sizes": textwrap.dedent("""\
            SELECT table_name, table_rows,
                   ROUND(data_length / 1024 / 1024, 2) AS data_mb,
                   ROUND(index_length / 1024 / 1024, 2) AS index_mb
            FROM information_schema.tables
            WHERE table_schema = DATABASE()
            ORDER BY data_length DESC;"""),
    },
    "sqlite": {
        "tables": textwrap.dedent("""\
            SELECT name FROM sqlite_master
            WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name;"""),
        "columns": textwrap.dedent("""\
            -- Run for each table:
            PRAGMA table_info({table_name});"""),
        "foreign_keys": textwrap.dedent("""\
            -- Run for each table:
            PRAGMA foreign_key_list({table_name});"""),
        "indexes": textwrap.dedent("""\
            SELECT name, tbl_name, sql FROM sqlite_master
            WHERE type = 'index'
            ORDER BY tbl_name, name;"""),
        "schema_dump": textwrap.dedent("""\
            SELECT name, sql FROM sqlite_master
            WHERE type = 'table'
            ORDER BY name;"""),
    },
    "sqlserver": {
        "tables": textwrap.dedent("""\
            SELECT TABLE_NAME
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_TYPE = 'BASE TABLE'
            ORDER BY TABLE_NAME;"""),
        "columns": textwrap.dedent("""\
            SELECT t.name AS table_name, c.name AS column_name,
                   ty.name AS data_type, c.max_length, c.precision, c.scale,
                   c.is_nullable, dc.definition AS default_value
            FROM sys.columns c
            JOIN sys.tables t ON c.object_id = t.object_id
            JOIN sys.types ty ON c.user_type_id = ty.user_type_id
            LEFT JOIN sys.default_constraints dc ON c.default_object_id = dc.object_id
            {table_filter}
            ORDER BY t.name, c.column_id;"""),
        "foreign_keys": textwrap.dedent("""\
            SELECT fk.name AS fk_name,
                   tp.name AS parent_table, cp.name AS parent_column,
                   tr.name AS referenced_table, cr.name AS referenced_column
            FROM sys.foreign_keys fk
            JOIN sys.foreign_key_columns fkc ON fk.object_id = fkc.constraint_object_id
            JOIN sys.tables tp ON fkc.parent_object_id = tp.object_id
            JOIN sys.columns cp ON fkc.parent_object_id = cp.object_id AND fkc.parent_column_id = cp.column_id
            JOIN sys.tables tr ON fkc.referenced_object_id = tr.object_id
            JOIN sys.columns cr ON fkc.referenced_object_id = cr.object_id AND fkc.referenced_column_id = cr.column_id
            ORDER BY tp.name;"""),
        "indexes": textwrap.dedent("""\
            SELECT t.name AS table_name, i.name AS index_name,
                   i.type_desc, i.is_unique, c.name AS column_name,
                   ic.key_ordinal
            FROM sys.indexes i
            JOIN sys.index_columns ic ON i.object_id = ic.object_id AND i.index_id = ic.index_id
            JOIN sys.columns c ON ic.object_id = c.object_id AND ic.column_id = c.column_id
            JOIN sys.tables t ON i.object_id = t.object_id
            WHERE i.name IS NOT NULL
            ORDER BY t.name, i.name, ic.key_ordinal;"""),
    },
}
