# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from upgrade_planner_base import *  # noqa: F403,E402
from upgrade_planner_p0 import DependencyUpgrade, UpdateType, UpgradePlan, UpgradeRisk  # noqa: F401,E501


class UpgradePlannerMixin6:
    def _suggest_mitigation_strategies(self, upgrades: List[DependencyUpgrade]) -> List[str]:
        """Suggest risk mitigation strategies."""
        strategies = []
        
        high_risk_count = len([u for u in upgrades if u.risk_level in [UpgradeRisk.HIGH, UpgradeRisk.CRITICAL]])
        if high_risk_count > 0:
            strategies.append("Create comprehensive test suite before high-risk upgrades")
            strategies.append("Plan rollback procedures for critical upgrades")
        
        major_count = len([u for u in upgrades if u.update_type == UpdateType.MAJOR])
        if major_count > 3:
            strategies.append("Phase major upgrades across multiple releases")
            strategies.append("Use feature flags for gradual rollout")
        
        security_count = len([u for u in upgrades if u.security_updates])
        if security_count > 0:
            strategies.append("Prioritize security updates regardless of risk level")
        
        return strategies
    def _create_upgrade_plans(self, upgrades: List[DependencyUpgrade], timeline_days: int) -> List[UpgradePlan]:
        """Create phased upgrade plans."""
        if not upgrades:
            return []
        
        # Sort upgrades by priority score (descending)
        sorted_upgrades = sorted(upgrades, key=lambda x: x.priority_score, reverse=True)
        
        plans = []
        
        # Phase 1: Security and safe updates (first 30% of timeline)
        phase1_upgrades = [u for u in sorted_upgrades if 
                          u.security_updates or u.risk_level == UpgradeRisk.SAFE][:10]
        if phase1_upgrades:
            plans.append(self._create_upgrade_plan(
                "Phase 1: Security & Safe Updates",
                "Immediate security fixes and low-risk updates",
                1, phase1_upgrades, timeline_days // 3
            ))
        
        # Phase 2: Low-medium risk updates (middle 40% of timeline)
        phase2_upgrades = [u for u in sorted_upgrades if 
                          u.risk_level in [UpgradeRisk.LOW, UpgradeRisk.MEDIUM] and
                          not u.security_updates][:8]
        if phase2_upgrades:
            plans.append(self._create_upgrade_plan(
                "Phase 2: Regular Updates",
                "Standard dependency updates with moderate risk",
                2, phase2_upgrades, timeline_days * 2 // 5
            ))
        
        # Phase 3: High-risk and major updates (final 30% of timeline)
        phase3_upgrades = [u for u in sorted_upgrades if 
                          u.risk_level in [UpgradeRisk.HIGH, UpgradeRisk.CRITICAL]][:5]
        if phase3_upgrades:
            plans.append(self._create_upgrade_plan(
                "Phase 3: Major Updates",
                "High-risk upgrades requiring careful planning",
                3, phase3_upgrades, timeline_days // 3
            ))
        
        return plans
