# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from rollback_generator_base import *  # noqa: F403,E402


class RollbackGeneratorMixin7:
    def _generate_emergency_contacts(self, migration_plan: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate emergency contact list"""
        return [
            {
                "role": "Incident Commander",
                "name": "TBD - Assigned during migration",
                "primary_phone": "+1-XXX-XXX-XXXX",
                "email": "incident.commander@company.com",
                "backup_contact": "backup.commander@company.com"
            },
            {
                "role": "Technical Lead",
                "name": "TBD - Migration technical owner",
                "primary_phone": "+1-XXX-XXX-XXXX",
                "email": "tech.lead@company.com",
                "backup_contact": "senior.engineer@company.com"
            },
            {
                "role": "Business Owner",
                "name": "TBD - Business stakeholder",
                "primary_phone": "+1-XXX-XXX-XXXX",
                "email": "business.owner@company.com",
                "backup_contact": "product.manager@company.com"
            },
            {
                "role": "On-Call Engineer",
                "name": "Current on-call rotation",
                "primary_phone": "+1-XXX-XXX-XXXX",
                "email": "oncall@company.com",
                "backup_contact": "backup.oncall@company.com"
            },
            {
                "role": "Executive Escalation",
                "name": "CTO/VP Engineering",
                "primary_phone": "+1-XXX-XXX-XXXX",
                "email": "cto@company.com",
                "backup_contact": "vp.engineering@company.com"
            }
        ]
    def _calculate_urgency(self, risk_level: str) -> str:
        """Calculate rollback urgency based on risk level"""
        risk_to_urgency = {
            "low": "low",
            "medium": "medium", 
            "high": "high",
            "critical": "emergency"
        }
        return risk_to_urgency.get(risk_level, "medium")
    def _get_rollback_prerequisites(self, phase_name: str, phase_index: int) -> List[str]:
        """Get prerequisites for rollback phase"""
        prerequisites = [
            "Incident commander assigned and briefed",
            "All team members notified of rollback initiation",
            "Monitoring systems confirmed operational",
            "Backup systems verified and accessible"
        ]
        
        if phase_index > 0:
            prerequisites.append("Previous rollback phase completed successfully")
        
        if "cutover" in phase_name.lower():
            prerequisites.extend([
                "Traffic redirection capabilities confirmed",
                "Load balancer configuration backed up",
                "DNS changes prepared for quick execution"
            ])
        
        if "data" in phase_name.lower() or "migration" in phase_name.lower():
            prerequisites.extend([
                "Database backup verified and accessible",
                "Data validation queries prepared",
                "Database administrator on standby"
            ])
        
        return prerequisites
    def _get_validation_checkpoints(self, phase_name: str, migration_type: str) -> List[str]:
        """Get validation checkpoints for rollback phase"""
        checkpoints = [
            f"{phase_name} rollback steps completed",
            "System health checks passing",
            "No critical errors in logs",
            "Key metrics within acceptable ranges"
        ]
        
        validation_commands = self.validation_templates.get(migration_type, [])
        checkpoints.extend([f"Validation command passed: {cmd[:50]}..." for cmd in validation_commands[:3]])
        
        return checkpoints
    def _get_communication_requirements(self, phase_name: str, risk_level: str) -> List[str]:
        """Get communication requirements for rollback phase"""
        base_requirements = [
            "Notify incident commander of phase start/completion",
            "Update rollback status dashboard",
            "Log all actions and decisions"
        ]
        
        if risk_level in ["high", "critical"]:
            base_requirements.extend([
                "Notify all stakeholders of phase progress",
                "Update executive team if rollback extends beyond expected time",
                "Prepare customer communication if needed"
            ])
        
        if "cutover" in phase_name.lower():
            base_requirements.append("Immediate notification when traffic is redirected")
        
        return base_requirements
