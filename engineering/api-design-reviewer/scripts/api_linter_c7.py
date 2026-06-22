# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from api_linter_base import *  # noqa: F403,E402


class APILinterMixin7:
    def generate_text_report(self) -> str:
        """Generate human-readable text report."""
        issues_by_severity = self.report.get_issues_by_severity()
        
        report_lines = [
            "═══════════════════════════════════════════════════════════════",
            "                      API LINTING REPORT",
            "═══════════════════════════════════════════════════════════════",
            "",
            "SUMMARY:",
            f"  Total Endpoints: {self.report.total_endpoints}",
            f"  Endpoints with Issues: {self.report.endpoints_with_issues}",
            f"  Overall Score: {self.report.score:.1f}/100.0",
            "",
            "ISSUE BREAKDOWN:",
            f"  🔴 Errors: {len(issues_by_severity['error'])}",
            f"  🟡 Warnings: {len(issues_by_severity['warning'])}",
            f"  ℹ️  Info: {len(issues_by_severity['info'])}",
            "",
        ]
        
        if not self.report.issues:
            report_lines.extend([
                "🎉 Congratulations! No issues found in your API specification.",
                ""
            ])
        else:
            # Group issues by category
            issues_by_category = {}
            for issue in self.report.issues:
                if issue.category not in issues_by_category:
                    issues_by_category[issue.category] = []
                issues_by_category[issue.category].append(issue)
            
            for category, issues in issues_by_category.items():
                report_lines.append(f"{'═' * 60}")
                report_lines.append(f"CATEGORY: {category.upper().replace('_', ' ')}")
                report_lines.append(f"{'═' * 60}")
                
                for issue in issues:
                    severity_icon = {"error": "🔴", "warning": "🟡", "info": "ℹ️"}[issue.severity]
                    
                    report_lines.extend([
                        f"{severity_icon} {issue.severity.upper()}: {issue.message}",
                        f"   Path: {issue.path}",
                    ])
                    
                    if issue.suggestion:
                        report_lines.append(f"   💡 Suggestion: {issue.suggestion}")
                    
                    report_lines.append("")
        
        # Add scoring breakdown
        report_lines.extend([
            "═══════════════════════════════════════════════════════════════",
            "SCORING DETAILS:",
            "═══════════════════════════════════════════════════════════════",
            f"Base Score: 100.0",
            f"Errors Penalty: -{len(issues_by_severity['error']) * 10} (10 points per error)",
            f"Warnings Penalty: -{len(issues_by_severity['warning']) * 3} (3 points per warning)",
            f"Info Penalty: -{len(issues_by_severity['info']) * 1} (1 point per info)",
            f"Final Score: {self.report.score:.1f}/100.0",
            ""
        ])
        
        # Add recommendations based on score
        if self.report.score >= 90:
            report_lines.append("🏆 Excellent! Your API design follows best practices.")
        elif self.report.score >= 80:
            report_lines.append("✅ Good API design with minor areas for improvement.")
        elif self.report.score >= 70:
            report_lines.append("⚠️  Fair API design. Consider addressing warnings and errors.")
        elif self.report.score >= 50:
            report_lines.append("❌ Poor API design. Multiple issues need attention.")
        else:
            report_lines.append("🚨 Critical API design issues. Immediate attention required.")
        
        return "\n".join(report_lines)
