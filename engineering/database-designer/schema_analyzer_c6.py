# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from schema_analyzer_base import *  # noqa: F403,E402


class SchemaAnalyzerMixin6:
    def get_analysis_summary(self) -> Dict[str, Any]:
        """Get comprehensive analysis summary."""
        return {
            "schema_overview": {
                "total_tables": len(self.tables),
                "total_columns": sum(len(table.columns) for table in self.tables.values()),
                "tables_with_primary_keys": len([t for t in self.tables.values() if t.primary_key]),
                "total_foreign_keys": sum(len(table.foreign_keys) for table in self.tables.values()),
                "total_indexes": sum(len(table.indexes) for table in self.tables.values())
            },
            "normalization_analysis": {
                "total_issues": len(self.normalization_issues),
                "by_severity": {
                    "high": len([i for i in self.normalization_issues if i.severity == "HIGH"]),
                    "medium": len([i for i in self.normalization_issues if i.severity == "MEDIUM"]),
                    "low": len([i for i in self.normalization_issues if i.severity == "LOW"]),
                    "warning": len([i for i in self.normalization_issues if i.severity == "WARNING"])
                },
                "issues": [asdict(issue) for issue in self.normalization_issues]
            },
            "data_type_analysis": {
                "total_issues": len(self.datatype_issues),
                "issues": [asdict(issue) for issue in self.datatype_issues]
            },
            "constraint_analysis": {
                "total_issues": len(self.constraint_issues),
                "by_severity": {
                    "high": len([i for i in self.constraint_issues if i.severity == "HIGH"]),
                    "medium": len([i for i in self.constraint_issues if i.severity == "MEDIUM"]),
                    "low": len([i for i in self.constraint_issues if i.severity == "LOW"])
                },
                "issues": [asdict(issue) for issue in self.constraint_issues]
            },
            "naming_analysis": {
                "total_issues": len(self.naming_issues),
                "issues": [asdict(issue) for issue in self.naming_issues]
            },
            "missing_indexes": self.check_missing_indexes(),
            "recommendations": self._generate_recommendations()
        }
    def _generate_recommendations(self) -> List[str]:
        """Generate high-level recommendations."""
        recommendations = []
        
        # High severity issues
        high_severity_issues = [
            i for i in self.normalization_issues + self.constraint_issues 
            if i.severity == "HIGH"
        ]
        
        if high_severity_issues:
            recommendations.append(f"Address {len(high_severity_issues)} high-severity issues immediately")
        
        # Missing primary keys
        tables_without_pk = [name for name, table in self.tables.items() if not table.primary_key]
        if tables_without_pk:
            recommendations.append(f"Add primary keys to tables: {', '.join(tables_without_pk)}")
        
        # Data type improvements
        varchar_255_issues = [i for i in self.datatype_issues if "VARCHAR(255)" in i.issue]
        if varchar_255_issues:
            recommendations.append(f"Review {len(varchar_255_issues)} VARCHAR(255) columns for right-sizing")
        
        # Missing foreign keys
        missing_fks = [i for i in self.constraint_issues if i.issue_type == "MISSING_FOREIGN_KEY"]
        if missing_fks:
            recommendations.append(f"Consider adding {len(missing_fks)} foreign key constraints for referential integrity")
        
        # Normalization improvements
        normalization_issues_count = len(self.normalization_issues)
        if normalization_issues_count > 0:
            recommendations.append(f"Review {normalization_issues_count} normalization issues for schema optimization")
        
        return recommendations
