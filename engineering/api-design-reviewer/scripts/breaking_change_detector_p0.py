# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from breaking_change_detector_base import *  # noqa: F403,E402


class ChangeType(Enum):
    """Types of API changes."""
    BREAKING = "breaking"
    POTENTIALLY_BREAKING = "potentially_breaking"
    NON_BREAKING = "non_breaking"
    ENHANCEMENT = "enhancement"


class ChangeSeverity(Enum):
    """Severity levels for changes."""
    CRITICAL = "critical"     # Will definitely break clients
    HIGH = "high"            # Likely to break some clients
    MEDIUM = "medium"        # May break clients depending on usage
    LOW = "low"             # Minor impact, unlikely to break clients
    INFO = "info"           # Informational, no breaking impact


@dataclass
class Change:
    """Represents a detected change between API versions."""
    change_type: ChangeType
    severity: ChangeSeverity
    category: str
    path: str
    message: str
    old_value: Any = None
    new_value: Any = None
    migration_guide: str = ""
    impact_description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert change to dictionary for JSON serialization."""
        return {
            "changeType": self.change_type.value,
            "severity": self.severity.value,
            "category": self.category,
            "path": self.path,
            "message": self.message,
            "oldValue": self.old_value,
            "newValue": self.new_value,
            "migrationGuide": self.migration_guide,
            "impactDescription": self.impact_description
        }


@dataclass
class ComparisonReport:
    """Complete comparison report between two API versions."""
    changes: List[Change] = field(default_factory=list)
    summary: Dict[str, int] = field(default_factory=dict)
    
    def add_change(self, change: Change) -> None:
        """Add a change to the report."""
        self.changes.append(change)
    
    def calculate_summary(self) -> None:
        """Calculate summary statistics."""
        self.summary = {
            "total_changes": len(self.changes),
            "breaking_changes": len([c for c in self.changes if c.change_type == ChangeType.BREAKING]),
            "potentially_breaking_changes": len([c for c in self.changes if c.change_type == ChangeType.POTENTIALLY_BREAKING]),
            "non_breaking_changes": len([c for c in self.changes if c.change_type == ChangeType.NON_BREAKING]),
            "enhancements": len([c for c in self.changes if c.change_type == ChangeType.ENHANCEMENT]),
            "critical_severity": len([c for c in self.changes if c.severity == ChangeSeverity.CRITICAL]),
            "high_severity": len([c for c in self.changes if c.severity == ChangeSeverity.HIGH]),
            "medium_severity": len([c for c in self.changes if c.severity == ChangeSeverity.MEDIUM]),
            "low_severity": len([c for c in self.changes if c.severity == ChangeSeverity.LOW]),
            "info_severity": len([c for c in self.changes if c.severity == ChangeSeverity.INFO])
        }
    
    def has_breaking_changes(self) -> bool:
        """Check if report contains any breaking changes."""
        return any(c.change_type in [ChangeType.BREAKING, ChangeType.POTENTIALLY_BREAKING] 
                  for c in self.changes)
