# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from upgrade_planner_base import *  # noqa: F403,E402
from upgrade_planner_p0 import UpdateType, UpgradeRisk, VersionInfo  # noqa: F401,E501


class UpgradePlannerMixin3:
    def _get_latest_version(self, package_name: str, ecosystem: str) -> Optional[str]:
        """Get latest version from package registry (simulated)."""
        # Simulated latest versions for common packages
        mock_versions = {
            'lodash': '4.17.21',
            'express': '4.18.2',
            'react': '18.2.0',
            'axios': '1.6.0',
            'django': '4.2.11',
            'requests': '2.31.0',
            'numpy': '1.24.0',
            'flask': '2.3.0',
            'fastapi': '0.104.0',
            'pytest': '7.4.0'
        }
        
        # In production, would query actual package registries:
        # npm: npm view <package> version
        # pypi: pip index versions <package>
        # maven: maven metadata API
        
        return mock_versions.get(package_name.lower())
    def _determine_update_type(self, current: VersionInfo, latest: VersionInfo) -> UpdateType:
        """Determine the type of update based on semantic versioning."""
        if latest.major > current.major:
            return UpdateType.MAJOR
        elif latest.minor > current.minor:
            return UpdateType.MINOR
        elif latest.patch > current.patch:
            return UpdateType.PATCH
        elif latest.prerelease and not current.prerelease:
            return UpdateType.PRERELEASE
        else:
            return UpdateType.PATCH  # Default fallback
    def _assess_upgrade_risk(self, package_name: str, current: VersionInfo, latest: VersionInfo,
                            ecosystem: str, update_type: UpdateType) -> UpgradeRisk:
        """Assess the risk level of an upgrade."""
        # Base risk assessment on update type
        base_risk = {
            UpdateType.PATCH: UpgradeRisk.SAFE,
            UpdateType.MINOR: UpgradeRisk.LOW,
            UpdateType.MAJOR: UpgradeRisk.HIGH,
            UpdateType.PRERELEASE: UpgradeRisk.MEDIUM
        }.get(update_type, UpgradeRisk.MEDIUM)
        
        # Adjust for package-specific factors
        high_risk_packages = [
            'webpack', 'babel', 'typescript', 'eslint',  # Build tools
            'react', 'vue', 'angular',  # Frameworks
            'django', 'flask', 'fastapi',  # Web frameworks
            'spring-boot', 'hibernate'  # Java frameworks
        ]
        
        if package_name.lower() in high_risk_packages and update_type == UpdateType.MAJOR:
            base_risk = UpgradeRisk.CRITICAL
        
        # Check for known breaking changes
        if self._has_known_breaking_changes(package_name, current, latest):
            if base_risk in [UpgradeRisk.SAFE, UpgradeRisk.LOW]:
                base_risk = UpgradeRisk.MEDIUM
            elif base_risk == UpgradeRisk.MEDIUM:
                base_risk = UpgradeRisk.HIGH
        
        return base_risk
    def _has_known_breaking_changes(self, package_name: str, current: VersionInfo, latest: VersionInfo) -> bool:
        """Check if there are known breaking changes between versions."""
        # Simulated breaking change detection
        breaking_change_versions = {
            'react': ['16.0.0', '17.0.0', '18.0.0'],
            'django': ['2.0.0', '3.0.0', '4.0.0'],
            'webpack': ['4.0.0', '5.0.0'],
            'babel': ['7.0.0', '8.0.0'],
            'typescript': ['4.0.0', '5.0.0']
        }
        
        package_versions = breaking_change_versions.get(package_name.lower(), [])
        latest_str = str(latest)
        
        return any(latest_str.startswith(v.split('.')[0]) for v in package_versions)
    def _check_security_updates(self, package_name: str, current_version: str, latest_version: str) -> List[str]:
        """Check for security updates in the upgrade."""
        security_updates = []
        
        if package_name in self.security_advisories:
            for advisory in self.security_advisories[package_name]:
                fixed_version = advisory['fixed_in']
                
                # Simple version comparison for security fixes
                if (self._is_version_greater(fixed_version, current_version) and
                    not self._is_version_greater(fixed_version, latest_version)):
                    security_updates.append(f"{advisory['advisory_id']}: {advisory['description']}")
        
        return security_updates
    def _is_version_greater(self, v1: str, v2: str) -> bool:
        """Simple version comparison."""
        v1_parts = [int(x) for x in v1.split('.')]
        v2_parts = [int(x) for x in v2.split('.')]
        
        # Pad shorter version
        max_len = max(len(v1_parts), len(v2_parts))
        v1_parts.extend([0] * (max_len - len(v1_parts)))
        v2_parts.extend([0] * (max_len - len(v2_parts)))
        
        return v1_parts > v2_parts
