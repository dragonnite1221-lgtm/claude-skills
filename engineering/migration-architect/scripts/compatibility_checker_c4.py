# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from compatibility_checker_base import *  # noqa: F403,E402
from compatibility_checker_p0 import CompatibilityIssue, MigrationScript  # noqa: F401,E501


class SchemaCompatibilityCheckerMixin4:
    def _analyze_column_changes(self, table_name: str, col_name: str, 
                              before_col: Dict[str, Any], after_col: Dict[str, Any]) -> Tuple[List[CompatibilityIssue], List[MigrationScript]]:
        """Analyze changes to a specific column"""
        issues = []
        scripts = []
        
        # Check data type changes
        before_type = before_col.get("type", "").lower()
        after_type = after_col.get("type", "").lower()
        
        if before_type != after_type:
            compatibility = self.type_compatibility_matrix.get(before_type, {}).get(after_type, "breaking")
            
            if compatibility == "breaking":
                issues.append(CompatibilityIssue(
                    type="incompatible_type_change",
                    severity="breaking",
                    description=f"Column '{col_name}' type changed from {before_type} to {after_type}",
                    field_path=f"tables.{table_name}.columns.{col_name}.type",
                    old_value=before_type,
                    new_value=after_type,
                    impact="Data conversion may fail or lose precision",
                    suggested_migration=f"Add conversion logic and validate data integrity",
                    affected_operations=["SELECT", "INSERT", "UPDATE", "WHERE clauses"]
                ))
                
                scripts.append(MigrationScript(
                    script_type="sql",
                    description=f"Convert column {col_name} from {before_type} to {after_type}",
                    script_content=f"ALTER TABLE {table_name} ALTER COLUMN {col_name} TYPE {after_type} USING {col_name}::{after_type};",
                    rollback_script=f"ALTER TABLE {table_name} ALTER COLUMN {col_name} TYPE {before_type};",
                    dependencies=[f"backup_{table_name}"],
                    validation_query=f"SELECT COUNT(*) FROM {table_name} WHERE {col_name} IS NOT NULL;"
                ))
            
            elif compatibility == "potentially_breaking":
                issues.append(CompatibilityIssue(
                    type="risky_type_change",
                    severity="potentially_breaking",
                    description=f"Column '{col_name}' type changed from {before_type} to {after_type} - may lose data",
                    field_path=f"tables.{table_name}.columns.{col_name}.type",
                    old_value=before_type,
                    new_value=after_type,
                    impact="Potential data loss or precision reduction",
                    suggested_migration=f"Validate all existing data can be converted safely",
                    affected_operations=["Data integrity"]
                ))
        
        # Check nullability changes
        before_nullable = before_col.get("nullable", True)
        after_nullable = after_col.get("nullable", True)
        
        if before_nullable != after_nullable:
            if before_nullable and not after_nullable:  # null -> not null
                issues.append(CompatibilityIssue(
                    type="nullability_restriction",
                    severity="breaking",
                    description=f"Column '{col_name}' changed from nullable to NOT NULL",
                    field_path=f"tables.{table_name}.columns.{col_name}.nullable",
                    old_value=before_nullable,
                    new_value=after_nullable,
                    impact="Existing NULL values will cause constraint violations",
                    suggested_migration=f"Update NULL values to valid defaults before applying NOT NULL constraint",
                    affected_operations=["INSERT", "UPDATE"]
                ))
                
                scripts.append(MigrationScript(
                    script_type="sql",
                    description=f"Make column {col_name} NOT NULL",
                    script_content=f"""
                    -- Update NULL values first
                    UPDATE {table_name} SET {col_name} = 'DEFAULT_VALUE' WHERE {col_name} IS NULL;
                    -- Add NOT NULL constraint
                    ALTER TABLE {table_name} ALTER COLUMN {col_name} SET NOT NULL;
                    """,
                    rollback_script=f"ALTER TABLE {table_name} ALTER COLUMN {col_name} DROP NOT NULL;",
                    dependencies=[],
                    validation_query=f"SELECT COUNT(*) FROM {table_name} WHERE {col_name} IS NULL;"
                ))
        
        # Check length/precision changes
        before_length = before_col.get("length")
        after_length = after_col.get("length")
        
        if before_length and after_length and before_length != after_length:
            if after_length < before_length:
                issues.append(CompatibilityIssue(
                    type="length_reduction",
                    severity="potentially_breaking",
                    description=f"Column '{col_name}' length reduced from {before_length} to {after_length}",
                    field_path=f"tables.{table_name}.columns.{col_name}.length",
                    old_value=before_length,
                    new_value=after_length,
                    impact="Data truncation may occur for values exceeding new length",
                    suggested_migration=f"Validate no existing data exceeds new length limit",
                    affected_operations=["INSERT", "UPDATE"]
                ))
        
        return issues, scripts
