# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from upgrade_planner_base import *  # noqa: F403,E402
from upgrade_planner_p0 import DependencyUpgrade, VersionInfo  # noqa: F401,E501


class UpgradePlannerMixin2:
    def _analyze_dependency_upgrade(self, dependency: Dict[str, Any]) -> Optional[DependencyUpgrade]:
        """Analyze upgrade possibilities for a single dependency."""
        name = dependency.get('name', '')
        current_version = dependency.get('version', '').replace('^', '').replace('~', '')
        ecosystem = dependency.get('ecosystem', '')
        
        if not name or not current_version:
            return None
        
        # Parse current version
        current_ver = self._parse_version(current_version)
        if not current_ver:
            return None
        
        # Get latest version (simulated - in practice would query package registries)
        latest_version = self._get_latest_version(name, ecosystem)
        if not latest_version:
            return None
        
        latest_ver = self._parse_version(latest_version)
        if not latest_ver:
            return None
        
        # Determine if upgrade is needed
        if self._compare_versions(current_ver, latest_ver) >= 0:
            return None  # Already up to date
        
        # Determine update type
        update_type = self._determine_update_type(current_ver, latest_ver)
        
        # Assess upgrade risk
        risk_level = self._assess_upgrade_risk(name, current_ver, latest_ver, ecosystem, update_type)
        
        # Check for security updates
        security_updates = self._check_security_updates(name, current_version, latest_version)
        
        # Analyze breaking changes
        breaking_changes = self._analyze_breaking_changes(name, current_ver, latest_ver, ecosystem)
        
        # Calculate priority score
        priority_score = self._calculate_priority_score(
            update_type, risk_level, security_updates, dependency.get('direct', False)
        )
        
        return DependencyUpgrade(
            name=name,
            current_version=current_version,
            latest_version=latest_version,
            ecosystem=ecosystem,
            direct=dependency.get('direct', False),
            update_type=update_type,
            risk_level=risk_level,
            security_updates=security_updates,
            breaking_changes=breaking_changes,
            migration_effort=self._estimate_migration_effort(update_type, breaking_changes),
            dependencies_affected=self._get_affected_dependencies(name, dependency),
            rollback_complexity=self._assess_rollback_complexity(update_type, risk_level),
            estimated_time=self._estimate_upgrade_time(update_type, breaking_changes),
            priority_score=priority_score
        )
    def _parse_version(self, version_string: str) -> Optional[VersionInfo]:
        """Parse semantic version string."""
        # Clean version string
        version = re.sub(r'[^0-9a-zA-Z.-]', '', version_string)
        
        # Basic semver pattern
        pattern = r'^(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z.-]+))?(?:\+([0-9A-Za-z.-]+))?$'
        match = re.match(pattern, version)
        
        if match:
            major, minor, patch, prerelease, build = match.groups()
            return VersionInfo(
                major=int(major),
                minor=int(minor),
                patch=int(patch),
                prerelease=prerelease,
                build=build
            )
        
        # Fallback for simpler version patterns
        simple_pattern = r'^(\d+)\.(\d+)(?:\.(\d+))?'
        match = re.match(simple_pattern, version)
        if match:
            major, minor, patch = match.groups()
            return VersionInfo(
                major=int(major),
                minor=int(minor),
                patch=int(patch or 0)
            )
        
        return None
    def _compare_versions(self, v1: VersionInfo, v2: VersionInfo) -> int:
        """Compare two versions. Returns -1, 0, or 1."""
        if (v1.major, v1.minor, v1.patch) < (v2.major, v2.minor, v2.patch):
            return -1
        elif (v1.major, v1.minor, v1.patch) > (v2.major, v2.minor, v2.patch):
            return 1
        else:
            # Handle prerelease comparison
            if v1.prerelease and not v2.prerelease:
                return -1
            elif not v1.prerelease and v2.prerelease:
                return 1
            elif v1.prerelease and v2.prerelease:
                if v1.prerelease < v2.prerelease:
                    return -1
                elif v1.prerelease > v2.prerelease:
                    return 1
            
            return 0
