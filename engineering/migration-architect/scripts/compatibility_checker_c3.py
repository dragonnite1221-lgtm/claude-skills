# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from compatibility_checker_base import *  # noqa: F403,E402
from compatibility_checker_p0 import CompatibilityIssue, MigrationScript  # noqa: F401,E501


class SchemaCompatibilityCheckerMixin3:
    def _analyze_table_changes(self, table_name: str, before_table: Dict[str, Any], 
                             after_table: Dict[str, Any]) -> Tuple[List[CompatibilityIssue], List[MigrationScript]]:
        """Analyze changes to a specific table"""
        issues = []
        scripts = []
        
        before_columns = before_table.get("columns", {})
        after_columns = after_table.get("columns", {})
        
        # Check for removed columns
        for col_name in before_columns:
            if col_name not in after_columns:
                issues.append(CompatibilityIssue(
                    type="column_removed",
                    severity="breaking",
                    description=f"Column '{col_name}' removed from table '{table_name}'",
                    field_path=f"tables.{table_name}.columns.{col_name}",
                    old_value=before_columns[col_name],
                    new_value=None,
                    impact="SELECT statements including this column will fail",
                    suggested_migration=f"ALTER TABLE {table_name} ADD COLUMN {col_name}_deprecated AS computed_value;",
                    affected_operations=["SELECT", "INSERT", "UPDATE"]
                ))
        
        # Check for added columns
        for col_name in after_columns:
            if col_name not in before_columns:
                col_def = after_columns[col_name]
                is_required = col_def.get("nullable", True) == False and col_def.get("default") is None
                
                if is_required:
                    issues.append(CompatibilityIssue(
                        type="required_column_added",
                        severity="breaking",
                        description=f"Required column '{col_name}' added to table '{table_name}'",
                        field_path=f"tables.{table_name}.columns.{col_name}",
                        old_value=None,
                        new_value=col_def,
                        impact="INSERT statements without this column will fail",
                        suggested_migration=f"Add default value or make column nullable initially",
                        affected_operations=["INSERT"]
                    ))
                
                scripts.append(MigrationScript(
                    script_type="sql",
                    description=f"Add column {col_name} to table {table_name}",
                    script_content=f"ALTER TABLE {table_name} ADD COLUMN {self._generate_column_definition(col_name, col_def)};",
                    rollback_script=f"ALTER TABLE {table_name} DROP COLUMN {col_name};",
                    dependencies=[],
                    validation_query=f"SELECT COUNT(*) FROM information_schema.columns WHERE table_name = '{table_name}' AND column_name = '{col_name}';"
                ))
        
        # Check for modified columns
        for col_name in set(before_columns.keys()) & set(after_columns.keys()):
            col_issues, col_scripts = self._analyze_column_changes(
                table_name, col_name, before_columns[col_name], after_columns[col_name]
            )
            issues.extend(col_issues)
            scripts.extend(col_scripts)
        
        # Check constraint changes
        before_constraints = before_table.get("constraints", {})
        after_constraints = after_table.get("constraints", {})
        
        constraint_issues, constraint_scripts = self._analyze_constraint_changes(
            table_name, before_constraints, after_constraints
        )
        issues.extend(constraint_issues)
        scripts.extend(constraint_scripts)
        
        return issues, scripts
