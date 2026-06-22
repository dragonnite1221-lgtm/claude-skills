# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from upgrade_planner_base import *  # noqa: F403,E402
from upgrade_planner_p0 import UpdateType, UpgradeRisk, VersionInfo  # noqa: F401,E501


class UpgradePlannerMixin4:
    def _analyze_breaking_changes(self, package_name: str, current: VersionInfo, 
                                 latest: VersionInfo, ecosystem: str) -> List[str]:
        """Analyze potential breaking changes."""
        breaking_changes = []
        
        # Check if major version change
        if latest.major > current.major:
            breaking_changes.append(f"Major version upgrade from {current.major}.x to {latest.major}.x")
            
            # Add ecosystem-specific common breaking changes
            ecosystem_knowledge = self.ecosystem_knowledge.get(ecosystem, {})
            common_changes = ecosystem_knowledge.get('common_breaking_changes', [])
            breaking_changes.extend(common_changes[:2])  # Add top 2
        
        # Check for specific package patterns
        if package_name.lower() == 'react' and latest.major >= 17:
            breaking_changes.append("New JSX Transform")
            if latest.major >= 18:
                breaking_changes.append("Concurrent Rendering changes")
        
        elif package_name.lower() == 'django' and latest.major >= 4:
            breaking_changes.append("CSRF token changes")
            breaking_changes.append("Default AUTO_INCREMENT field changes")
        
        elif package_name.lower() == 'webpack' and latest.major >= 5:
            breaking_changes.append("Module Federation support")
            breaking_changes.append("Asset modules replace file-loader")
        
        return breaking_changes
    def _calculate_priority_score(self, update_type: UpdateType, risk_level: UpgradeRisk,
                                 security_updates: List[str], is_direct: bool) -> float:
        """Calculate priority score for upgrade (0-100)."""
        score = 50.0  # Base score
        
        # Security updates get highest priority
        if security_updates:
            score += 30.0
            score += len(security_updates) * 5.0  # Multiple security fixes
        
        # Update type scoring
        type_scores = {
            UpdateType.PATCH: 20.0,
            UpdateType.MINOR: 10.0,
            UpdateType.MAJOR: -10.0,
            UpdateType.PRERELEASE: -5.0
        }
        score += type_scores.get(update_type, 0)
        
        # Risk level adjustment
        risk_adjustments = {
            UpgradeRisk.SAFE: 15.0,
            UpgradeRisk.LOW: 5.0,
            UpgradeRisk.MEDIUM: -5.0,
            UpgradeRisk.HIGH: -15.0,
            UpgradeRisk.CRITICAL: -25.0
        }
        score += risk_adjustments.get(risk_level, 0)
        
        # Direct dependencies get slightly higher priority
        if is_direct:
            score += 5.0
        
        return max(0.0, min(100.0, score))
    def _estimate_migration_effort(self, update_type: UpdateType, breaking_changes: List[str]) -> str:
        """Estimate migration effort level."""
        if update_type == UpdateType.PATCH and not breaking_changes:
            return "Minimal"
        elif update_type == UpdateType.MINOR and len(breaking_changes) <= 1:
            return "Low"
        elif update_type == UpdateType.MAJOR or len(breaking_changes) > 2:
            return "High"
        else:
            return "Medium"
    def _get_affected_dependencies(self, package_name: str, dependency: Dict[str, Any]) -> List[str]:
        """Get list of dependencies that might be affected by this upgrade."""
        # Simulated dependency impact analysis
        common_dependencies = {
            'react': ['react-dom', 'react-router', 'react-redux'],
            'django': ['djangorestframework', 'django-cors-headers', 'celery'],
            'webpack': ['webpack-cli', 'webpack-dev-server', 'html-webpack-plugin'],
            'babel': ['@babel/core', '@babel/preset-env', '@babel/preset-react']
        }
        
        return common_dependencies.get(package_name.lower(), [])
    def _assess_rollback_complexity(self, update_type: UpdateType, risk_level: UpgradeRisk) -> str:
        """Assess complexity of rolling back the upgrade."""
        if update_type == UpdateType.PATCH:
            return "Simple"
        elif update_type == UpdateType.MINOR and risk_level in [UpgradeRisk.SAFE, UpgradeRisk.LOW]:
            return "Simple"
        elif risk_level in [UpgradeRisk.HIGH, UpgradeRisk.CRITICAL]:
            return "Complex"
        else:
            return "Moderate"
