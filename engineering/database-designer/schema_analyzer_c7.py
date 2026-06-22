# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from schema_analyzer_base import *  # noqa: F403,E402


class SchemaAnalyzerMixin7:
    def format_text_report(self, analysis: Dict[str, Any]) -> str:
        """Format analysis as human-readable text report."""
        lines = []
        lines.append("DATABASE SCHEMA ANALYSIS REPORT")
        lines.append("=" * 50)
        lines.append("")
        
        # Overview
        overview = analysis["schema_overview"]
        lines.append("SCHEMA OVERVIEW")
        lines.append("-" * 15)
        lines.append(f"Total Tables: {overview['total_tables']}")
        lines.append(f"Total Columns: {overview['total_columns']}")
        lines.append(f"Tables with Primary Keys: {overview['tables_with_primary_keys']}")
        lines.append(f"Total Foreign Keys: {overview['total_foreign_keys']}")
        lines.append(f"Total Indexes: {overview['total_indexes']}")
        lines.append("")
        
        # Recommendations
        if analysis["recommendations"]:
            lines.append("KEY RECOMMENDATIONS")
            lines.append("-" * 18)
            for i, rec in enumerate(analysis["recommendations"], 1):
                lines.append(f"{i}. {rec}")
            lines.append("")
        
        # Normalization Issues
        norm_analysis = analysis["normalization_analysis"]
        if norm_analysis["total_issues"] > 0:
            lines.append(f"NORMALIZATION ISSUES ({norm_analysis['total_issues']} total)")
            lines.append("-" * 25)
            severity_counts = norm_analysis["by_severity"]
            lines.append(f"High: {severity_counts['high']}, Medium: {severity_counts['medium']}, "
                        f"Low: {severity_counts['low']}, Warning: {severity_counts['warning']}")
            lines.append("")
            
            for issue in norm_analysis["issues"][:5]:  # Show first 5
                lines.append(f"• {issue['table']}: {issue['description']}")
                lines.append(f"  Suggestion: {issue['suggestion']}")
                lines.append("")
        
        # Data Type Issues
        dt_analysis = analysis["data_type_analysis"]
        if dt_analysis["total_issues"] > 0:
            lines.append(f"DATA TYPE ISSUES ({dt_analysis['total_issues']} total)")
            lines.append("-" * 20)
            for issue in dt_analysis["issues"][:5]:  # Show first 5
                lines.append(f"• {issue['table']}.{issue['column']}: {issue['issue']}")
                lines.append(f"  Current: {issue['current_type']} → Suggested: {issue['suggested_type']}")
                lines.append(f"  Rationale: {issue['rationale']}")
                lines.append("")
        
        # Constraint Issues
        const_analysis = analysis["constraint_analysis"]
        if const_analysis["total_issues"] > 0:
            lines.append(f"CONSTRAINT ISSUES ({const_analysis['total_issues']} total)")
            lines.append("-" * 20)
            severity_counts = const_analysis["by_severity"]
            lines.append(f"High: {severity_counts['high']}, Medium: {severity_counts['medium']}, "
                        f"Low: {severity_counts['low']}")
            lines.append("")
            
            for issue in const_analysis["issues"][:5]:  # Show first 5
                lines.append(f"• {issue['table']}: {issue['description']}")
                lines.append(f"  Suggestion: {issue['suggestion']}")
                lines.append("")
        
        # Missing Indexes
        missing_idx = analysis["missing_indexes"]
        if missing_idx:
            lines.append(f"MISSING INDEXES ({len(missing_idx)} total)")
            lines.append("-" * 17)
            for idx in missing_idx[:5]:  # Show first 5
                lines.append(f"• {idx['table']}.{idx['column']} ({idx['type']})")
                lines.append(f"  SQL: {idx['suggestion']}")
                lines.append("")
        
        return "\n".join(lines)
