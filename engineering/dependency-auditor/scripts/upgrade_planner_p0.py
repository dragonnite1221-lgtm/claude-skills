# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from upgrade_planner_base import *  # noqa: F403,E402


class UpgradeRisk(Enum):
    """Upgrade risk levels."""
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class UpdateType(Enum):
    """Semantic versioning update types."""
    PATCH = "patch"
    MINOR = "minor"
    MAJOR = "major"
    PRERELEASE = "prerelease"


@dataclass
class VersionInfo:
    """Represents version information."""
    major: int
    minor: int
    patch: int
    prerelease: Optional[str] = None
    build: Optional[str] = None
    
    def __str__(self):
        version = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            version += f"-{self.prerelease}"
        if self.build:
            version += f"+{self.build}"
        return version


@dataclass
class DependencyUpgrade:
    """Represents a potential dependency upgrade."""
    name: str
    current_version: str
    latest_version: str
    ecosystem: str
    direct: bool
    update_type: UpdateType
    risk_level: UpgradeRisk
    security_updates: List[str]
    breaking_changes: List[str]
    migration_effort: str
    dependencies_affected: List[str]
    rollback_complexity: str
    estimated_time: str
    priority_score: float


@dataclass
class UpgradePlan:
    """Represents a complete upgrade plan."""
    name: str
    description: str
    phase: int
    dependencies: List[str]
    estimated_duration: str
    prerequisites: List[str]
    migration_steps: List[str]
    testing_requirements: List[str]
    rollback_plan: List[str]
    success_criteria: List[str]
