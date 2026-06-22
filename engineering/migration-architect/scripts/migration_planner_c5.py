# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from migration_planner_base import *  # noqa: F403,E402
from migration_planner_p0 import MigrationPlan  # noqa: F401,E501


class MigrationPlannerMixin5:
    def generate_human_readable_plan(self, plan: MigrationPlan) -> str:
        """Generate human-readable migration plan"""
        output = []
        output.append("=" * 80)
        output.append(f"MIGRATION PLAN: {plan.migration_id}")
        output.append("=" * 80)
        output.append(f"Source System: {plan.source_system}")
        output.append(f"Target System: {plan.target_system}")
        output.append(f"Migration Type: {plan.migration_type.upper()}")
        output.append(f"Complexity Level: {plan.complexity.upper()}")
        output.append(f"Estimated Duration: {plan.estimated_duration_hours} hours ({plan.estimated_duration_hours/24:.1f} days)")
        output.append(f"Created: {plan.created_at}")
        output.append("")
        
        # Phases
        output.append("MIGRATION PHASES")
        output.append("-" * 40)
        for i, phase in enumerate(plan.phases, 1):
            output.append(f"{i}. {phase.name.upper()} ({phase.duration_hours}h)")
            output.append(f"   Description: {phase.description}")
            output.append(f"   Risk Level: {phase.risk_level.upper()}")
            if phase.dependencies:
                output.append(f"   Dependencies: {', '.join(phase.dependencies)}")
            output.append("   Tasks:")
            for task in phase.tasks:
                output.append(f"     • {task}")
            output.append("   Success Criteria:")
            for criteria in phase.validation_criteria:
                output.append(f"     ✓ {criteria}")
            output.append("")
        
        # Risk Assessment
        output.append("RISK ASSESSMENT")
        output.append("-" * 40)
        risk_by_severity = {}
        for risk in plan.risks:
            if risk.severity not in risk_by_severity:
                risk_by_severity[risk.severity] = []
            risk_by_severity[risk.severity].append(risk)
        
        for severity in ["critical", "high", "medium", "low"]:
            if severity in risk_by_severity:
                output.append(f"{severity.upper()} SEVERITY RISKS:")
                for risk in risk_by_severity[severity]:
                    output.append(f"  • {risk.description}")
                    output.append(f"    Category: {risk.category}")
                    output.append(f"    Probability: {risk.probability} | Impact: {risk.impact}")
                    output.append(f"    Mitigation: {risk.mitigation}")
                    output.append(f"    Owner: {risk.owner}")
                    output.append("")
        
        # Rollback Plan
        output.append("ROLLBACK STRATEGY")
        output.append("-" * 40)
        output.append("Rollback Triggers:")
        for trigger in plan.rollback_plan["rollback_triggers"]:
            output.append(f"  • {trigger}")
        output.append("")
        
        output.append("Rollback Phases:")
        for rb_phase in plan.rollback_plan["rollback_phases"]:
            output.append(f"  {rb_phase['phase'].upper()}:")
            for action in rb_phase["rollback_actions"]:
                output.append(f"    - {action}")
            output.append(f"    Estimated Time: {rb_phase['estimated_time_minutes']} minutes")
            output.append("")
        
        # Success Criteria
        output.append("SUCCESS CRITERIA")
        output.append("-" * 40)
        for criteria in plan.success_criteria:
            output.append(f"✓ {criteria}")
        output.append("")
        
        # Stakeholders
        output.append("STAKEHOLDERS")
        output.append("-" * 40)
        for stakeholder in plan.stakeholders:
            output.append(f"• {stakeholder}")
        output.append("")
        
        return "\n".join(output)
