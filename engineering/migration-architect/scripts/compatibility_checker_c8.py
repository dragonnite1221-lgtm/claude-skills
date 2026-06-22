# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from compatibility_checker_base import *  # noqa: F403,E402
from compatibility_checker_p0 import CompatibilityIssue, CompatibilityReport, MigrationScript  # noqa: F401,E501


class SchemaCompatibilityCheckerMixin8:
    def _build_compatibility_report(self, before_schema: Dict[str, Any], after_schema: Dict[str, Any],
                                  issues: List[CompatibilityIssue], migration_scripts: List[MigrationScript]) -> CompatibilityReport:
        """Build the final compatibility report"""
        # Count issues by severity
        breaking_count = sum(1 for issue in issues if issue.severity == "breaking")
        potentially_breaking_count = sum(1 for issue in issues if issue.severity == "potentially_breaking")
        non_breaking_count = sum(1 for issue in issues if issue.severity == "non_breaking")
        additive_count = sum(1 for issue in issues if issue.type == "additive")
        
        # Determine overall compatibility
        if breaking_count > 0:
            overall_compatibility = "breaking_changes"
        elif potentially_breaking_count > 0:
            overall_compatibility = "potentially_incompatible"
        elif non_breaking_count > 0:
            overall_compatibility = "backward_compatible"
        else:
            overall_compatibility = "fully_compatible"
        
        # Generate risk assessment
        risk_assessment = {
            "overall_risk": "high" if breaking_count > 0 else "medium" if potentially_breaking_count > 0 else "low",
            "deployment_risk": "requires_coordinated_deployment" if breaking_count > 0 else "safe_independent_deployment",
            "rollback_complexity": "high" if breaking_count > 3 else "medium" if breaking_count > 0 else "low",
            "testing_requirements": ["integration_testing", "regression_testing"] + 
                                  (["data_migration_testing"] if any(s.script_type == "sql" for s in migration_scripts) else [])
        }
        
        # Generate recommendations
        recommendations = []
        if breaking_count > 0:
            recommendations.append("Implement API versioning to maintain backward compatibility")
            recommendations.append("Plan for coordinated deployment with all clients")
            recommendations.append("Implement comprehensive rollback procedures")
        
        if potentially_breaking_count > 0:
            recommendations.append("Conduct thorough testing with realistic data volumes")
            recommendations.append("Implement monitoring for migration success metrics")
        
        if migration_scripts:
            recommendations.append("Test all migration scripts in staging environment")
            recommendations.append("Implement migration progress monitoring")
        
        recommendations.append("Create detailed communication plan for stakeholders")
        recommendations.append("Implement feature flags for gradual rollout")
        
        return CompatibilityReport(
            schema_before=json.dumps(before_schema, indent=2)[:500] + "..." if len(json.dumps(before_schema)) > 500 else json.dumps(before_schema, indent=2),
            schema_after=json.dumps(after_schema, indent=2)[:500] + "..." if len(json.dumps(after_schema)) > 500 else json.dumps(after_schema, indent=2),
            analysis_date=datetime.datetime.now().isoformat(),
            overall_compatibility=overall_compatibility,
            breaking_changes_count=breaking_count,
            potentially_breaking_count=potentially_breaking_count,
            non_breaking_changes_count=non_breaking_count,
            additive_changes_count=additive_count,
            issues=issues,
            migration_scripts=migration_scripts,
            risk_assessment=risk_assessment,
            recommendations=recommendations
        )
    def _generate_create_table_sql(self, table_name: str, table_def: Dict[str, Any]) -> str:
        """Generate CREATE TABLE SQL statement"""
        columns = []
        for col_name, col_def in table_def.get("columns", {}).items():
            columns.append(self._generate_column_definition(col_name, col_def))
        
        return f"CREATE TABLE {table_name} (\n  " + ",\n  ".join(columns) + "\n);"
    def _generate_column_definition(self, col_name: str, col_def: Dict[str, Any]) -> str:
        """Generate column definition for SQL"""
        col_type = col_def.get("type", "VARCHAR(255)")
        nullable = "" if col_def.get("nullable", True) else " NOT NULL"
        default = f" DEFAULT {col_def.get('default')}" if col_def.get("default") is not None else ""
        
        return f"{col_name} {col_type}{nullable}{default}"
