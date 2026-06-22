# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from skill_validator_base import *  # noqa: F403,E402
from skill_validator_p0 import ValidationReport  # noqa: F401,E501


class ReportFormatter:
    """Formats validation reports for output"""
    
    @staticmethod
    def format_json(report: ValidationReport) -> str:
        """Format report as JSON"""
        return json.dumps({
            "skill_path": report.skill_path,
            "timestamp": report.timestamp,
            "overall_score": round(report.overall_score, 1),
            "compliance_level": report.compliance_level,
            "checks": report.checks,
            "warnings": report.warnings,
            "errors": report.errors,
            "suggestions": report.suggestions
        }, indent=2)
        
    @staticmethod
    def format_human_readable(report: ValidationReport) -> str:
        """Format report as human-readable text"""
        lines = []
        lines.append("=" * 60)
        lines.append("SKILL VALIDATION REPORT")
        lines.append("=" * 60)
        lines.append(f"Skill: {report.skill_path}")
        lines.append(f"Timestamp: {report.timestamp}")
        lines.append(f"Overall Score: {report.overall_score:.1f}/100 ({report.compliance_level})")
        lines.append("")
        
        # Group checks by category
        structure_checks = {k: v for k, v in report.checks.items() if k.startswith(('skill_md', 'readme', 'dir_'))}
        script_checks = {k: v for k, v in report.checks.items() if k.startswith('script_')}
        other_checks = {k: v for k, v in report.checks.items() if k not in structure_checks and k not in script_checks}
        
        if structure_checks:
            lines.append("STRUCTURE VALIDATION:")
            for check_name, result in structure_checks.items():
                status = "✓ PASS" if result["passed"] else "✗ FAIL"
                lines.append(f"  {status}: {result['message']}")
            lines.append("")
            
        if script_checks:
            lines.append("SCRIPT VALIDATION:")
            for check_name, result in script_checks.items():
                status = "✓ PASS" if result["passed"] else "✗ FAIL"
                lines.append(f"  {status}: {result['message']}")
            lines.append("")
            
        if other_checks:
            lines.append("OTHER CHECKS:")
            for check_name, result in other_checks.items():
                status = "✓ PASS" if result["passed"] else "✗ FAIL"
                lines.append(f"  {status}: {result['message']}")
            lines.append("")
            
        if report.errors:
            lines.append("ERRORS:")
            for error in report.errors:
                lines.append(f"  • {error}")
            lines.append("")
            
        if report.warnings:
            lines.append("WARNINGS:")
            for warning in report.warnings:
                lines.append(f"  • {warning}")
            lines.append("")
            
        if report.suggestions:
            lines.append("SUGGESTIONS:")
            for suggestion in report.suggestions:
                lines.append(f"  • {suggestion}")
            lines.append("")
            
        return "\n".join(lines)
