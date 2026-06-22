# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from upgrade_planner_base import *  # noqa: F403,E402
from upgrade_planner_p0 import UpgradeRisk  # noqa: F401,E501


class UpgradePlannerMixin8:
    def generate_report(self, analysis_results: Dict[str, Any], format: str = 'text') -> str:
        """Generate upgrade plan report in specified format."""
        if format == 'json':
            # Convert dataclass objects for JSON serialization
            serializable_results = analysis_results.copy()
            serializable_results['available_upgrades'] = [asdict(upgrade) for upgrade in analysis_results['available_upgrades']]
            serializable_results['upgrade_plans'] = [asdict(plan) for plan in analysis_results['upgrade_plans']]
            return json.dumps(serializable_results, indent=2, default=str)
        
        # Text format report
        report = []
        report.append("=" * 60)
        report.append("DEPENDENCY UPGRADE PLAN")
        report.append("=" * 60)
        report.append(f"Generated: {analysis_results['timestamp']}")
        report.append(f"Timeline: {analysis_results['timeline_days']} days")
        report.append("")
        
        # Statistics
        stats = analysis_results['upgrade_statistics']
        report.append("UPGRADE SUMMARY:")
        report.append(f"  Total Upgrades Available: {stats.get('total_upgrades', 0)}")
        report.append(f"  Security Updates: {stats.get('security_updates', 0)}")
        report.append(f"  Major Version Updates: {stats['by_type'].get('major', 0)}")
        report.append(f"  High Risk Updates: {stats['by_risk'].get('high', 0)}")
        report.append("")
        
        # Risk Assessment
        risk = analysis_results['risk_assessment']
        report.append("RISK ASSESSMENT:")
        report.append(f"  Overall Risk Level: {risk['overall_risk']}")
        if risk.get('risk_factors'):
            report.append("  Key Risk Factors:")
            for factor in risk['risk_factors'][:3]:
                report.append(f"    • {factor}")
        report.append("")
        
        # High Priority Upgrades
        high_priority = sorted([u for u in analysis_results['available_upgrades']], 
                              key=lambda x: x.priority_score, reverse=True)[:10]
        
        if high_priority:
            report.append("TOP PRIORITY UPGRADES:")
            report.append("-" * 30)
            for upgrade in high_priority:
                risk_indicator = "🔴" if upgrade.risk_level in [UpgradeRisk.HIGH, UpgradeRisk.CRITICAL] else \
                               "🟡" if upgrade.risk_level == UpgradeRisk.MEDIUM else "🟢"
                security_indicator = " 🔒" if upgrade.security_updates else ""
                
                report.append(f"{risk_indicator} {upgrade.name}: {upgrade.current_version} → {upgrade.latest_version}{security_indicator}")
                report.append(f"   Type: {upgrade.update_type.value.title()} | Risk: {upgrade.risk_level.value.title()} | Priority: {upgrade.priority_score:.1f}")
                if upgrade.security_updates:
                    report.append(f"   Security: {upgrade.security_updates[0]}")
                report.append("")
        
        # Upgrade Plans
        if analysis_results['upgrade_plans']:
            report.append("PHASED UPGRADE PLANS:")
            report.append("-" * 30)
            
            for plan in analysis_results['upgrade_plans']:
                report.append(f"{plan.name} ({plan.estimated_duration})")
                report.append(f"  Dependencies: {', '.join(plan.dependencies[:5])}")
                if len(plan.dependencies) > 5:
                    report.append(f"  ... and {len(plan.dependencies) - 5} more")
                report.append(f"  Key Steps: {'; '.join(plan.migration_steps[:3])}")
                report.append("")
        
        # Recommendations
        if analysis_results['recommendations']:
            report.append("RECOMMENDATIONS:")
            report.append("-" * 20)
            for i, rec in enumerate(analysis_results['recommendations'], 1):
                report.append(f"{i}. {rec}")
            report.append("")
        
        report.append("=" * 60)
        return '\n'.join(report)
