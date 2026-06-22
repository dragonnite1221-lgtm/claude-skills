# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from compatibility_checker_base import *  # noqa: F403,E402
from compatibility_checker_p0 import CompatibilityIssue, MigrationScript  # noqa: F401,E501


class SchemaCompatibilityCheckerMixin5:
    def _analyze_constraint_changes(self, table_name: str, before_constraints: Dict[str, Any], 
                                  after_constraints: Dict[str, Any]) -> Tuple[List[CompatibilityIssue], List[MigrationScript]]:
        """Analyze constraint changes"""
        issues = []
        scripts = []
        
        for constraint_type in ["primary_key", "foreign_key", "unique", "check"]:
            before_constraint = before_constraints.get(constraint_type, [])
            after_constraint = after_constraints.get(constraint_type, [])
            
            # Convert to sets for comparison
            before_set = set(str(c) for c in before_constraint) if isinstance(before_constraint, list) else {str(before_constraint)} if before_constraint else set()
            after_set = set(str(c) for c in after_constraint) if isinstance(after_constraint, list) else {str(after_constraint)} if after_constraint else set()
            
            # Check for removed constraints
            for constraint in before_set - after_set:
                implication = self.constraint_implications.get(constraint_type, {}).get("removed", "non_breaking")
                issues.append(CompatibilityIssue(
                    type=f"{constraint_type}_removed",
                    severity=implication,
                    description=f"{constraint_type.replace('_', ' ').title()} constraint '{constraint}' removed from table '{table_name}'",
                    field_path=f"tables.{table_name}.constraints.{constraint_type}",
                    old_value=constraint,
                    new_value=None,
                    impact=f"No longer enforcing {constraint_type} constraint",
                    suggested_migration=f"Consider application-level validation for removed constraint",
                    affected_operations=["INSERT", "UPDATE", "DELETE"]
                ))
            
            # Check for added constraints
            for constraint in after_set - before_set:
                implication = self.constraint_implications.get(constraint_type, {}).get("added", "potentially_breaking")
                issues.append(CompatibilityIssue(
                    type=f"{constraint_type}_added",
                    severity=implication,
                    description=f"New {constraint_type.replace('_', ' ')} constraint '{constraint}' added to table '{table_name}'",
                    field_path=f"tables.{table_name}.constraints.{constraint_type}",
                    old_value=None,
                    new_value=constraint,
                    impact=f"New {constraint_type} constraint may reject existing data",
                    suggested_migration=f"Validate existing data complies with new constraint",
                    affected_operations=["INSERT", "UPDATE"]
                ))
                
                scripts.append(MigrationScript(
                    script_type="sql",
                    description=f"Add {constraint_type} constraint to {table_name}",
                    script_content=f"ALTER TABLE {table_name} ADD CONSTRAINT {constraint_type}_{table_name} {constraint_type.upper()} ({constraint});",
                    rollback_script=f"ALTER TABLE {table_name} DROP CONSTRAINT {constraint_type}_{table_name};",
                    dependencies=[],
                    validation_query=f"SELECT COUNT(*) FROM information_schema.table_constraints WHERE table_name = '{table_name}' AND constraint_type = '{constraint_type.upper()}';"
                ))
        
        return issues, scripts
