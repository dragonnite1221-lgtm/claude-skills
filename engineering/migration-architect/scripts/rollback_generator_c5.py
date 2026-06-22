# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from rollback_generator_base import *  # noqa: F403,E402
from rollback_generator_p0 import CommunicationTemplate, DataRecoveryPlan  # noqa: F401,E501


class RollbackGeneratorMixin5:
    def _generate_data_recovery_plan(self, migration_plan: Dict[str, Any]) -> DataRecoveryPlan:
        """Generate data recovery plan"""
        migration_type = migration_plan.get("migration_type", "unknown")
        
        if migration_type == "database":
            return DataRecoveryPlan(
                recovery_method="point_in_time",
                backup_location="/backups/pre_migration_{migration_id}_{timestamp}.sql",
                recovery_scripts=[
                    "pg_restore -d production -c /backups/pre_migration_backup.sql",
                    "SELECT pg_create_restore_point('rollback_point');",
                    "VACUUM ANALYZE; -- Refresh statistics after restore"
                ],
                data_validation_queries=[
                    "SELECT COUNT(*) FROM critical_business_table;",
                    "SELECT MAX(created_at) FROM audit_log;",
                    "SELECT COUNT(DISTINCT user_id) FROM user_sessions;",
                    "SELECT SUM(amount) FROM financial_transactions WHERE date = CURRENT_DATE;"
                ],
                estimated_recovery_time_minutes=45,
                recovery_dependencies=["database_instance_running", "backup_file_accessible"]
            )
        else:
            return DataRecoveryPlan(
                recovery_method="backup_restore",
                backup_location="/backups/pre_migration_state",
                recovery_scripts=[
                    "# Restore configuration files from backup",
                    "cp -r /backups/pre_migration_state/config/* /app/config/",
                    "# Restart services with previous configuration",
                    "systemctl restart application_service"
                ],
                data_validation_queries=[
                    "curl -f http://localhost:8080/health",
                    "curl -f http://localhost:8080/api/status"
                ],
                estimated_recovery_time_minutes=20,
                recovery_dependencies=["service_stopped", "backup_accessible"]
            )
    def _generate_communication_templates(self, migration_plan: Dict[str, Any]) -> List[CommunicationTemplate]:
        """Generate communication templates for rollback scenarios"""
        templates = []
        base_templates = self.communication_templates
        
        # Rollback start notifications
        for audience in ["technical", "business", "executive"]:
            if audience in base_templates["rollback_start"]:
                template_data = base_templates["rollback_start"][audience]
                templates.append(CommunicationTemplate(
                    template_type="rollback_start",
                    audience=audience,
                    subject=template_data["subject"],
                    body=template_data["body"],
                    urgency="high" if audience == "executive" else "medium",
                    delivery_methods=["email", "slack"] if audience == "technical" else ["email"]
                ))
        
        # Rollback completion notifications
        for audience in ["technical", "business"]:
            if audience in base_templates.get("rollback_complete", {}):
                template_data = base_templates["rollback_complete"][audience]
                templates.append(CommunicationTemplate(
                    template_type="rollback_complete",
                    audience=audience,
                    subject=template_data["subject"],
                    body=template_data["body"],
                    urgency="medium",
                    delivery_methods=["email", "slack"] if audience == "technical" else ["email"]
                ))
        
        # Emergency escalation template
        templates.append(CommunicationTemplate(
            template_type="emergency_escalation",
            audience="executive",
            subject="CRITICAL: Rollback Emergency - {migration_name}",
            body="""CRITICAL SITUATION - IMMEDIATE ATTENTION REQUIRED

Migration: {migration_name}
Issue: Rollback procedure has encountered critical failures

Current Status: {current_status}
Failed Components: {failed_components}
Business Impact: {business_impact}
Customer Impact: {customer_impact}

Immediate Actions:
1. Emergency response team activated
2. {emergency_action_1}
3. {emergency_action_2}

War Room: {war_room_location}
Bridge Line: {conference_bridge}

Next Update: {next_update_time}

Incident Commander: {incident_commander}
Executive On-Call: {executive_on_call}
""",
            urgency="emergency",
            delivery_methods=["email", "sms", "phone_call"]
        ))
        
        return templates
