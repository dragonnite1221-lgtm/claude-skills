# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from breaking_change_detector_base import *  # noqa: F403,E402
from breaking_change_detector_p0 import ChangeType  # noqa: F401,E501


class BreakingChangeDetectorMixin8:
    def generate_text_report(self) -> str:
        """Generate human-readable text report."""
        lines = [
            "═══════════════════════════════════════════════════════════════",
            "                  BREAKING CHANGE ANALYSIS REPORT",
            "═══════════════════════════════════════════════════════════════",
            "",
            "SUMMARY:",
            f"  Total Changes: {self.report.summary.get('total_changes', 0)}",
            f"  🔴 Breaking Changes: {self.report.summary.get('breaking_changes', 0)}",
            f"  🟡 Potentially Breaking: {self.report.summary.get('potentially_breaking_changes', 0)}",
            f"  🟢 Non-Breaking Changes: {self.report.summary.get('non_breaking_changes', 0)}",
            f"  ✨ Enhancements: {self.report.summary.get('enhancements', 0)}",
            "",
            "SEVERITY BREAKDOWN:",
            f"  🚨 Critical: {self.report.summary.get('critical_severity', 0)}",
            f"  ⚠️  High: {self.report.summary.get('high_severity', 0)}",
            f"  ⚪ Medium: {self.report.summary.get('medium_severity', 0)}",
            f"  🔵 Low: {self.report.summary.get('low_severity', 0)}",
            f"  ℹ️  Info: {self.report.summary.get('info_severity', 0)}",
            ""
        ]
        
        if not self.report.changes:
            lines.extend([
                "🎉 No changes detected between the API versions!",
                ""
            ])
        else:
            # Group changes by type and severity
            breaking_changes = [c for c in self.report.changes if c.change_type == ChangeType.BREAKING]
            potentially_breaking = [c for c in self.report.changes if c.change_type == ChangeType.POTENTIALLY_BREAKING]
            non_breaking = [c for c in self.report.changes if c.change_type == ChangeType.NON_BREAKING]
            enhancements = [c for c in self.report.changes if c.change_type == ChangeType.ENHANCEMENT]
            
            # Breaking changes section
            if breaking_changes:
                lines.extend([
                    "🔴 BREAKING CHANGES:",
                    "═" * 60
                ])
                for change in sorted(breaking_changes, key=lambda x: x.severity.value):
                    self._add_change_to_report(lines, change)
                lines.append("")
            
            # Potentially breaking changes section
            if potentially_breaking:
                lines.extend([
                    "🟡 POTENTIALLY BREAKING CHANGES:",
                    "═" * 60
                ])
                for change in sorted(potentially_breaking, key=lambda x: x.severity.value):
                    self._add_change_to_report(lines, change)
                lines.append("")
            
            # Non-breaking changes section
            if non_breaking:
                lines.extend([
                    "🟢 NON-BREAKING CHANGES:",
                    "═" * 60
                ])
                for change in non_breaking:
                    self._add_change_to_report(lines, change)
                lines.append("")
            
            # Enhancements section
            if enhancements:
                lines.extend([
                    "✨ ENHANCEMENTS:",
                    "═" * 60
                ])
                for change in enhancements:
                    self._add_change_to_report(lines, change)
                lines.append("")
        
        # Add overall assessment
        lines.extend([
            "═══════════════════════════════════════════════════════════════",
            "OVERALL ASSESSMENT:",
            "═══════════════════════════════════════════════════════════════"
        ])
        
        if self.report.has_breaking_changes():
            breaking_count = self.report.summary.get('breaking_changes', 0)
            potentially_breaking_count = self.report.summary.get('potentially_breaking_changes', 0)
            
            if breaking_count > 0:
                lines.extend([
                    f"⛔ MAJOR VERSION BUMP REQUIRED",
                    f"   This API version contains {breaking_count} breaking changes that will",
                    f"   definitely break existing clients. A major version bump is required.",
                    ""
                ])
            elif potentially_breaking_count > 0:
                lines.extend([
                    f"⚠️  MINOR VERSION BUMP RECOMMENDED",
                    f"   This API version contains {potentially_breaking_count} potentially breaking",
                    f"   changes. Consider a minor version bump and communicate changes to clients.",
                    ""
                ])
        else:
            lines.extend([
                "✅ PATCH VERSION BUMP ACCEPTABLE",
                "   No breaking changes detected. This version is backward compatible",
                "   with existing clients.",
                ""
            ])
        
        return "\n".join(lines)
