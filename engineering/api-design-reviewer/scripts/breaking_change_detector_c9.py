# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from breaking_change_detector_base import *  # noqa: F403,E402
from breaking_change_detector_p0 import Change, ChangeSeverity  # noqa: F401,E501


class BreakingChangeDetectorMixin9:
    def _add_change_to_report(self, lines: List[str], change: Change) -> None:
        """Add a change to the text report."""
        severity_icons = {
            ChangeSeverity.CRITICAL: "🚨",
            ChangeSeverity.HIGH: "⚠️ ",
            ChangeSeverity.MEDIUM: "⚪",
            ChangeSeverity.LOW: "🔵",
            ChangeSeverity.INFO: "ℹ️ "
        }
        
        icon = severity_icons.get(change.severity, "❓")
        
        lines.extend([
            f"{icon} {change.severity.value.upper()}: {change.message}",
            f"   Path: {change.path}",
            f"   Category: {change.category}"
        ])
        
        if change.impact_description:
            lines.append(f"   Impact: {change.impact_description}")
        
        if change.migration_guide:
            lines.append(f"   💡 Migration: {change.migration_guide}")
        
        lines.append("")
