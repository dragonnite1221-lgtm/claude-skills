# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from compatibility_checker_base import *  # noqa: F403,E402
from compatibility_checker_p0 import CompatibilityReport  # noqa: F401,E501


class SchemaCompatibilityCheckerMixin9:
    def generate_human_readable_report(self, report: CompatibilityReport) -> str:
        """Generate human-readable compatibility report"""
        output = []
        output.append("=" * 80)
        output.append("COMPATIBILITY ANALYSIS REPORT")
        output.append("=" * 80)
        output.append(f"Analysis Date: {report.analysis_date}")
        output.append(f"Overall Compatibility: {report.overall_compatibility.upper()}")
        output.append("")
        
        # Summary
        output.append("SUMMARY")
        output.append("-" * 40)
        output.append(f"Breaking Changes: {report.breaking_changes_count}")
        output.append(f"Potentially Breaking: {report.potentially_breaking_count}")
        output.append(f"Non-Breaking Changes: {report.non_breaking_changes_count}")
        output.append(f"Additive Changes: {report.additive_changes_count}")
        output.append(f"Total Issues Found: {len(report.issues)}")
        output.append("")
        
        # Risk Assessment
        output.append("RISK ASSESSMENT")
        output.append("-" * 40)
        for key, value in report.risk_assessment.items():
            output.append(f"{key.replace('_', ' ').title()}: {value}")
        output.append("")
        
        # Issues by Severity
        issues_by_severity = {}
        for issue in report.issues:
            if issue.severity not in issues_by_severity:
                issues_by_severity[issue.severity] = []
            issues_by_severity[issue.severity].append(issue)
        
        for severity in ["breaking", "potentially_breaking", "non_breaking"]:
            if severity in issues_by_severity:
                output.append(f"{severity.upper().replace('_', ' ')} ISSUES")
                output.append("-" * 40)
                for issue in issues_by_severity[severity]:
                    output.append(f"• {issue.description}")
                    output.append(f"  Field: {issue.field_path}")
                    output.append(f"  Impact: {issue.impact}")
                    output.append(f"  Migration: {issue.suggested_migration}")
                    if issue.affected_operations:
                        output.append(f"  Affected Operations: {', '.join(issue.affected_operations)}")
                    output.append("")
        
        # Migration Scripts
        if report.migration_scripts:
            output.append("SUGGESTED MIGRATION SCRIPTS")
            output.append("-" * 40)
            for i, script in enumerate(report.migration_scripts, 1):
                output.append(f"{i}. {script.description}")
                output.append(f"   Type: {script.script_type}")
                output.append("   Script:")
                for line in script.script_content.split('\n'):
                    output.append(f"     {line}")
                output.append("")
        
        # Recommendations
        output.append("RECOMMENDATIONS")
        output.append("-" * 40)
        for i, rec in enumerate(report.recommendations, 1):
            output.append(f"{i}. {rec}")
        output.append("")
        
        return "\n".join(output)
