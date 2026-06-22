# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from compatibility_checker_base import *  # noqa: F403,E402
from compatibility_checker_p0 import CompatibilityIssue, CompatibilityReport, MigrationScript  # noqa: F401,E501


class SchemaCompatibilityCheckerMixin1:
    def _build_constraint_implications(self) -> Dict[str, Dict[str, str]]:
        """Build constraint change implications"""
        return {
            "required": {
                "added": "breaking",  # Previously optional field now required
                "removed": "non_breaking"  # Previously required field now optional
            },
            "not_null": {
                "added": "breaking",  # Previously nullable now NOT NULL
                "removed": "non_breaking"  # Previously NOT NULL now nullable
            },
            "unique": {
                "added": "potentially_breaking",  # May fail if duplicates exist
                "removed": "non_breaking"  # No longer enforcing uniqueness
            },
            "primary_key": {
                "added": "breaking",  # Major structural change
                "removed": "breaking",  # Major structural change
                "modified": "breaking"  # Primary key change is always breaking
            },
            "foreign_key": {
                "added": "potentially_breaking",  # May fail if referential integrity violated
                "removed": "potentially_breaking",  # May allow orphaned records
                "modified": "breaking"  # Reference change is breaking
            },
            "check": {
                "added": "potentially_breaking",  # May fail if existing data violates check
                "removed": "non_breaking",  # No longer enforcing check
                "modified": "potentially_breaking"  # Different validation rules
            },
            "index": {
                "added": "non_breaking",  # Performance improvement
                "removed": "non_breaking",  # Performance impact only
                "modified": "non_breaking"  # Performance impact only
            }
        }
    def analyze_database_schema(self, before_schema: Dict[str, Any], 
                              after_schema: Dict[str, Any]) -> CompatibilityReport:
        """Analyze database schema compatibility"""
        issues = []
        migration_scripts = []
        
        before_tables = before_schema.get("tables", {})
        after_tables = after_schema.get("tables", {})
        
        # Check for removed tables
        for table_name in before_tables:
            if table_name not in after_tables:
                issues.append(CompatibilityIssue(
                    type="table_removed",
                    severity="breaking",
                    description=f"Table '{table_name}' has been removed",
                    field_path=f"tables.{table_name}",
                    old_value=before_tables[table_name],
                    new_value=None,
                    impact="All operations on this table will fail",
                    suggested_migration=f"CREATE VIEW {table_name} AS SELECT * FROM replacement_table;",
                    affected_operations=["SELECT", "INSERT", "UPDATE", "DELETE"]
                ))
        
        # Check for added tables
        for table_name in after_tables:
            if table_name not in before_tables:
                migration_scripts.append(MigrationScript(
                    script_type="sql",
                    description=f"Create new table {table_name}",
                    script_content=self._generate_create_table_sql(table_name, after_tables[table_name]),
                    rollback_script=f"DROP TABLE IF EXISTS {table_name};",
                    dependencies=[],
                    validation_query=f"SELECT COUNT(*) FROM information_schema.tables WHERE table_name = '{table_name}';"
                ))
        
        # Check for modified tables
        for table_name in set(before_tables.keys()) & set(after_tables.keys()):
            table_issues, table_scripts = self._analyze_table_changes(
                table_name, before_tables[table_name], after_tables[table_name]
            )
            issues.extend(table_issues)
            migration_scripts.extend(table_scripts)
        
        return self._build_compatibility_report(
            before_schema, after_schema, issues, migration_scripts
        )
