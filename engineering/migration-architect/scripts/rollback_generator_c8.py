# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from rollback_generator_base import *  # noqa: F403,E402
from rollback_generator_p0 import RollbackRunbook  # noqa: F401,E501


class RollbackGeneratorMixin8:
    def generate_human_readable_runbook(self, runbook: RollbackRunbook) -> str:
        """Generate human-readable rollback runbook"""
        output = []
        output.append("=" * 80)
        output.append(f"ROLLBACK RUNBOOK: {runbook.runbook_id}")
        output.append("=" * 80)
        output.append(f"Migration ID: {runbook.migration_id}")
        output.append(f"Created: {runbook.created_at}")
        output.append("")
        
        # Emergency Contacts
        output.append("EMERGENCY CONTACTS")
        output.append("-" * 40)
        for contact in runbook.emergency_contacts:
            output.append(f"{contact['role']}: {contact['name']}")
            output.append(f"  Phone: {contact['primary_phone']}")
            output.append(f"  Email: {contact['email']}")
            output.append(f"  Backup: {contact['backup_contact']}")
            output.append("")
        
        # Escalation Matrix
        output.append("ESCALATION MATRIX")
        output.append("-" * 40)
        for level, details in runbook.escalation_matrix.items():
            output.append(f"{level.upper()}:")
            output.append(f"  Trigger: {details['trigger']}")
            output.append(f"  Response Time: {details['response_time_minutes']} minutes")
            output.append(f"  Contacts: {', '.join(details['contacts'])}")
            output.append(f"  Actions: {', '.join(details['actions'])}")
            output.append("")
        
        # Rollback Trigger Conditions
        output.append("AUTOMATIC ROLLBACK TRIGGERS")
        output.append("-" * 40)
        for trigger in runbook.trigger_conditions:
            output.append(f"• {trigger.name}")
            output.append(f"  Condition: {trigger.condition}")
            output.append(f"  Auto-Execute: {'Yes' if trigger.auto_execute else 'No'}")
            output.append(f"  Evaluation Window: {trigger.evaluation_window_minutes} minutes")
            output.append(f"  Contacts: {', '.join(trigger.escalation_contacts)}")
            output.append("")
        
        # Rollback Phases
        output.append("ROLLBACK PHASES")
        output.append("-" * 40)
        for i, phase in enumerate(runbook.rollback_phases, 1):
            output.append(f"{i}. {phase.phase_name.upper()}")
            output.append(f"   Description: {phase.description}")
            output.append(f"   Urgency: {phase.urgency_level.upper()}")
            output.append(f"   Duration: {phase.estimated_duration_minutes} minutes")
            output.append(f"   Risk Level: {phase.risk_level.upper()}")
            
            if phase.prerequisites:
                output.append("   Prerequisites:")
                for prereq in phase.prerequisites:
                    output.append(f"     ✓ {prereq}")
            
            output.append("   Steps:")
            for step in sorted(phase.steps, key=lambda x: x.rollback_order):
                output.append(f"     {step.rollback_order}. {step.name}")
                output.append(f"        Duration: {step.estimated_duration_minutes} min")
                output.append(f"        Type: {step.script_type}")
                if step.script_content and step.script_type != "manual":
                    output.append("        Script:")
                    for line in step.script_content.split('\n')[:3]:  # Show first 3 lines
                        output.append(f"          {line}")
                    if len(step.script_content.split('\n')) > 3:
                        output.append("          ...")
                output.append(f"        Success Criteria: {', '.join(step.success_criteria)}")
                output.append("")
            
            if phase.validation_checkpoints:
                output.append("   Validation Checkpoints:")
                for checkpoint in phase.validation_checkpoints:
                    output.append(f"     ☐ {checkpoint}")
            output.append("")
        
        # Data Recovery Plan
        output.append("DATA RECOVERY PLAN")
        output.append("-" * 40)
        drp = runbook.data_recovery_plan
        output.append(f"Recovery Method: {drp.recovery_method}")
        output.append(f"Backup Location: {drp.backup_location}")
        output.append(f"Estimated Recovery Time: {drp.estimated_recovery_time_minutes} minutes")
        output.append("Recovery Scripts:")
        for script in drp.recovery_scripts:
            output.append(f"  • {script}")
        output.append("Validation Queries:")
        for query in drp.data_validation_queries:
            output.append(f"  • {query}")
        output.append("")
        
        # Validation Checklist
        output.append("POST-ROLLBACK VALIDATION CHECKLIST")
        output.append("-" * 40)
        for i, item in enumerate(runbook.validation_checklist, 1):
            output.append(f"{i:2d}. ☐ {item}")
        output.append("")
        
        # Post-Rollback Procedures
        output.append("POST-ROLLBACK PROCEDURES")
        output.append("-" * 40)
        for i, procedure in enumerate(runbook.post_rollback_procedures, 1):
            output.append(f"{i:2d}. {procedure}")
        output.append("")
        
        return "\n".join(output)
