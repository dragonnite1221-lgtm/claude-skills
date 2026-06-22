# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from compatibility_checker_base import *  # noqa: F403,E402


class ChangeType(Enum):
    """Types of changes detected"""
    BREAKING = "breaking"
    POTENTIALLY_BREAKING = "potentially_breaking"
    NON_BREAKING = "non_breaking"
    ADDITIVE = "additive"


class CompatibilityLevel(Enum):
    """Compatibility assessment levels"""
    FULLY_COMPATIBLE = "fully_compatible"
    BACKWARD_COMPATIBLE = "backward_compatible"
    POTENTIALLY_INCOMPATIBLE = "potentially_incompatible"
    BREAKING_CHANGES = "breaking_changes"


@dataclass
class CompatibilityIssue:
    """Individual compatibility issue"""
    type: str
    severity: str
    description: str
    field_path: str
    old_value: Any
    new_value: Any
    impact: str
    suggested_migration: str
    affected_operations: List[str]


@dataclass
class MigrationScript:
    """Migration script suggestion"""
    script_type: str  # sql, api, config
    description: str
    script_content: str
    rollback_script: str
    dependencies: List[str]
    validation_query: str


@dataclass
class CompatibilityReport:
    """Complete compatibility analysis report"""
    schema_before: str
    schema_after: str
    analysis_date: str
    overall_compatibility: str
    breaking_changes_count: int
    potentially_breaking_count: int
    non_breaking_changes_count: int
    additive_changes_count: int
    issues: List[CompatibilityIssue]
    migration_scripts: List[MigrationScript]
    risk_assessment: Dict[str, Any]
    recommendations: List[str]
