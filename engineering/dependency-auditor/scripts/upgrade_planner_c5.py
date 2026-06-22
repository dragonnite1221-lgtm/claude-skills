# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from upgrade_planner_base import *  # noqa: F403,E402
from upgrade_planner_p0 import DependencyUpgrade, UpdateType, UpgradeRisk  # noqa: F401,E501


class UpgradePlannerMixin5:
    def _estimate_upgrade_time(self, update_type: UpdateType, breaking_changes: List[str]) -> str:
        """Estimate time required for upgrade."""
        base_times = {
            UpdateType.PATCH: "30 minutes",
            UpdateType.MINOR: "2 hours",
            UpdateType.MAJOR: "1 day",
            UpdateType.PRERELEASE: "4 hours"
        }
        
        base_time = base_times.get(update_type, "4 hours")
        
        if len(breaking_changes) > 2:
            if "30 minutes" in base_time:
                base_time = "2 hours"
            elif "2 hours" in base_time:
                base_time = "1 day"
            elif "1 day" in base_time:
                base_time = "3 days"
        
        return base_time
    def _generate_upgrade_statistics(self, upgrades: List[DependencyUpgrade]) -> Dict[str, Any]:
        """Generate statistics about available upgrades."""
        if not upgrades:
            return {}
        
        return {
            'total_upgrades': len(upgrades),
            'by_type': {
                'patch': len([u for u in upgrades if u.update_type == UpdateType.PATCH]),
                'minor': len([u for u in upgrades if u.update_type == UpdateType.MINOR]),
                'major': len([u for u in upgrades if u.update_type == UpdateType.MAJOR]),
                'prerelease': len([u for u in upgrades if u.update_type == UpdateType.PRERELEASE])
            },
            'by_risk': {
                'safe': len([u for u in upgrades if u.risk_level == UpgradeRisk.SAFE]),
                'low': len([u for u in upgrades if u.risk_level == UpgradeRisk.LOW]),
                'medium': len([u for u in upgrades if u.risk_level == UpgradeRisk.MEDIUM]),
                'high': len([u for u in upgrades if u.risk_level == UpgradeRisk.HIGH]),
                'critical': len([u for u in upgrades if u.risk_level == UpgradeRisk.CRITICAL])
            },
            'security_updates': len([u for u in upgrades if u.security_updates]),
            'direct_dependencies': len([u for u in upgrades if u.direct]),
            'average_priority': sum(u.priority_score for u in upgrades) / len(upgrades)
        }
    def _perform_risk_assessment(self, upgrades: List[DependencyUpgrade]) -> Dict[str, Any]:
        """Perform comprehensive risk assessment."""
        high_risk_upgrades = [u for u in upgrades if u.risk_level in [UpgradeRisk.HIGH, UpgradeRisk.CRITICAL]]
        security_upgrades = [u for u in upgrades if u.security_updates]
        major_upgrades = [u for u in upgrades if u.update_type == UpdateType.MAJOR]
        
        return {
            'overall_risk': self._calculate_overall_upgrade_risk(upgrades),
            'high_risk_count': len(high_risk_upgrades),
            'security_critical_count': len(security_upgrades),
            'major_version_count': len(major_upgrades),
            'risk_factors': self._identify_risk_factors(upgrades),
            'mitigation_strategies': self._suggest_mitigation_strategies(upgrades)
        }
    def _calculate_overall_upgrade_risk(self, upgrades: List[DependencyUpgrade]) -> str:
        """Calculate overall risk level for all upgrades."""
        if not upgrades:
            return "LOW"
        
        risk_scores = {
            UpgradeRisk.SAFE: 1,
            UpgradeRisk.LOW: 2,
            UpgradeRisk.MEDIUM: 3,
            UpgradeRisk.HIGH: 4,
            UpgradeRisk.CRITICAL: 5
        }
        
        total_score = sum(risk_scores.get(u.risk_level, 3) for u in upgrades)
        average_score = total_score / len(upgrades)
        
        if average_score >= 4.0:
            return "CRITICAL"
        elif average_score >= 3.0:
            return "HIGH"
        elif average_score >= 2.0:
            return "MEDIUM"
        else:
            return "LOW"
    def _identify_risk_factors(self, upgrades: List[DependencyUpgrade]) -> List[str]:
        """Identify key risk factors across all upgrades."""
        factors = []
        
        major_count = len([u for u in upgrades if u.update_type == UpdateType.MAJOR])
        if major_count > 0:
            factors.append(f"{major_count} major version upgrades with potential breaking changes")
        
        critical_count = len([u for u in upgrades if u.risk_level == UpgradeRisk.CRITICAL])
        if critical_count > 0:
            factors.append(f"{critical_count} critical risk upgrades requiring careful planning")
        
        framework_upgrades = [u for u in upgrades if any(fw in u.name.lower() 
                             for fw in ['react', 'django', 'spring', 'webpack', 'babel'])]
        if framework_upgrades:
            factors.append(f"Core framework upgrades: {[u.name for u in framework_upgrades[:3]]}")
        
        return factors
