# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from upgrade_planner_base import *  # noqa: F403,E402
from upgrade_planner_p0 import DependencyUpgrade, UpgradePlan, UpgradeRisk  # noqa: F401,E501


class UpgradePlannerMixin7:
    def _create_upgrade_plan(self, name: str, description: str, phase: int,
                            upgrades: List[DependencyUpgrade], duration_days: int) -> UpgradePlan:
        """Create a detailed upgrade plan for a phase."""
        dependency_names = [u.name for u in upgrades]
        
        # Generate migration steps
        migration_steps = []
        migration_steps.append("1. Create feature branch for upgrades")
        migration_steps.append("2. Update dependency versions in manifest files")
        migration_steps.append("3. Run dependency install/update commands")
        migration_steps.append("4. Fix breaking changes and deprecation warnings")
        migration_steps.append("5. Update test suite for compatibility")
        migration_steps.append("6. Run comprehensive test suite")
        migration_steps.append("7. Update documentation and changelog")
        migration_steps.append("8. Create pull request for review")
        
        # Add phase-specific steps
        if phase == 1:
            migration_steps.insert(3, "3a. Verify security fixes are applied")
        elif phase == 3:
            migration_steps.insert(5, "5a. Perform extensive integration testing")
            migration_steps.insert(6, "6a. Test with production-like data")
        
        # Generate testing requirements
        testing_requirements = [
            "Unit test suite passes 100%",
            "Integration tests cover upgrade scenarios",
            "Performance benchmarks within acceptable range"
        ]
        
        if any(u.risk_level in [UpgradeRisk.HIGH, UpgradeRisk.CRITICAL] for u in upgrades):
            testing_requirements.extend([
                "Manual testing of critical user flows",
                "Load testing for performance regression",
                "Security scanning for new vulnerabilities"
            ])
        
        # Generate rollback plan
        rollback_plan = [
            "1. Revert dependency versions in manifest files",
            "2. Run dependency install with previous versions",
            "3. Restore previous configuration files if changed",
            "4. Run smoke tests to verify rollback success",
            "5. Monitor system health metrics"
        ]
        
        # Success criteria
        success_criteria = [
            "All tests pass in CI/CD pipeline",
            "No security vulnerabilities introduced",
            "Performance metrics within acceptable thresholds",
            "No critical user workflows broken"
        ]
        
        return UpgradePlan(
            name=name,
            description=description,
            phase=phase,
            dependencies=dependency_names,
            estimated_duration=f"{duration_days} days",
            prerequisites=self._generate_prerequisites(upgrades),
            migration_steps=migration_steps,
            testing_requirements=testing_requirements,
            rollback_plan=rollback_plan,
            success_criteria=success_criteria
        )
    def _generate_prerequisites(self, upgrades: List[DependencyUpgrade]) -> List[str]:
        """Generate prerequisites for upgrade phase."""
        prerequisites = [
            "Comprehensive test suite with good coverage",
            "Backup of current working state",
            "Development environment setup"
        ]
        
        if any(u.risk_level in [UpgradeRisk.HIGH, UpgradeRisk.CRITICAL] for u in upgrades):
            prerequisites.extend([
                "Staging environment for testing",
                "Rollback procedure documented and tested",
                "Team availability for issue resolution"
            ])
        
        if any(u.security_updates for u in upgrades):
            prerequisites.append("Security team notification for validation")
        
        return prerequisites
    def _generate_upgrade_recommendations(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Generate actionable upgrade recommendations."""
        recommendations = []
        
        security_count = analysis_results['upgrade_statistics'].get('security_updates', 0)
        if security_count > 0:
            recommendations.append(f"URGENT: {security_count} security updates available - prioritize immediately")
        
        safe_count = analysis_results['upgrade_statistics']['by_risk'].get('safe', 0)
        if safe_count > 0:
            recommendations.append(f"Quick wins: {safe_count} safe updates can be applied with minimal risk")
        
        critical_count = analysis_results['risk_assessment']['high_risk_count']
        if critical_count > 0:
            recommendations.append(f"Plan carefully: {critical_count} high-risk upgrades need thorough testing")
        
        major_count = analysis_results['upgrade_statistics']['by_type'].get('major', 0)
        if major_count > 3:
            recommendations.append("Consider phasing major upgrades across multiple releases")
        
        overall_risk = analysis_results['risk_assessment']['overall_risk']
        if overall_risk in ['HIGH', 'CRITICAL']:
            recommendations.append("Overall upgrade risk is high - recommend gradual approach")
        
        return recommendations
