# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from rollback_generator_base import *  # noqa: F403,E402
from rollback_generator_p0 import RollbackStep  # noqa: F401,E501


class RollbackGeneratorMixin3:
    def _generate_rollback_steps(self, phase_name: str, migration_type: str, phase_index: int) -> List[RollbackStep]:
        """Generate specific rollback steps for a phase"""
        steps = []
        templates = self.rollback_templates.get(migration_type, {})
        
        if migration_type == "database":
            if "migration" in phase_name.lower() or "cutover" in phase_name.lower():
                # Data rollback steps
                steps.extend([
                    RollbackStep(
                        step_id=f"rb_data_{phase_index}_01",
                        name="Stop data migration processes",
                        description="Halt all ongoing data migration processes",
                        script_type="sql",
                        script_content="-- Stop migration processes\nSELECT pg_cancel_backend(pid) FROM pg_stat_activity WHERE query LIKE '%migration%';",
                        estimated_duration_minutes=5,
                        dependencies=[],
                        validation_commands=["SELECT COUNT(*) FROM pg_stat_activity WHERE query LIKE '%migration%';"],
                        success_criteria=["No active migration processes"],
                        failure_escalation="Contact DBA immediately",
                        rollback_order=1
                    ),
                    RollbackStep(
                        step_id=f"rb_data_{phase_index}_02",
                        name="Restore from backup",
                        description="Restore database from pre-migration backup",
                        script_type="bash",
                        script_content=templates.get("data_rollback", {}).get("restore_backup", "pg_restore -d {database_name} -c {backup_file}"),
                        estimated_duration_minutes=30,
                        dependencies=[f"rb_data_{phase_index}_01"],
                        validation_commands=["SELECT COUNT(*) FROM information_schema.tables;"],
                        success_criteria=["Database restored successfully", "All expected tables present"],
                        failure_escalation="Escalate to senior DBA and infrastructure team",
                        rollback_order=2
                    )
                ])
            
            if "preparation" in phase_name.lower():
                # Schema rollback steps
                steps.append(
                    RollbackStep(
                        step_id=f"rb_schema_{phase_index}_01",
                        name="Drop migration artifacts",
                        description="Remove temporary migration tables and procedures",
                        script_type="sql",
                        script_content="-- Drop migration artifacts\nDROP TABLE IF EXISTS migration_log;\nDROP PROCEDURE IF EXISTS migrate_data();",
                        estimated_duration_minutes=5,
                        dependencies=[],
                        validation_commands=["SELECT COUNT(*) FROM information_schema.tables WHERE table_name LIKE '%migration%';"],
                        success_criteria=["No migration artifacts remain"],
                        failure_escalation="Manual cleanup required",
                        rollback_order=1
                    )
                )
        
        elif migration_type == "service":
            if "cutover" in phase_name.lower():
                # Service rollback steps
                steps.extend([
                    RollbackStep(
                        step_id=f"rb_service_{phase_index}_01",
                        name="Redirect traffic back to old service",
                        description="Update load balancer to route traffic back to previous service version",
                        script_type="bash",
                        script_content=templates.get("deployment_rollback", {}).get("update_load_balancer", "aws elbv2 modify-rule --rule-arn {rule_arn} --actions Type=forward,TargetGroupArn={original_target_group}"),
                        estimated_duration_minutes=2,
                        dependencies=[],
                        validation_commands=["curl -f {health_check_url}"],
                        success_criteria=["Traffic routing to original service", "Health checks passing"],
                        failure_escalation="Emergency procedure - manual traffic routing",
                        rollback_order=1
                    ),
                    RollbackStep(
                        step_id=f"rb_service_{phase_index}_02",
                        name="Rollback service deployment",
                        description="Revert to previous service deployment version",
                        script_type="bash",
                        script_content=templates.get("deployment_rollback", {}).get("restore_previous_version", "kubectl rollout undo deployment/{service_name} --to-revision={revision_number}"),
                        estimated_duration_minutes=10,
                        dependencies=[f"rb_service_{phase_index}_01"],
                        validation_commands=["kubectl get pods -l app={service_name} --field-selector=status.phase=Running"],
                        success_criteria=["Previous version deployed", "All pods running"],
                        failure_escalation="Manual pod management required",
                        rollback_order=2
                    )
                ])
        
        elif migration_type == "infrastructure":
            steps.extend([
                RollbackStep(
                    step_id=f"rb_infra_{phase_index}_01",
                    name="Revert infrastructure changes",
                    description="Apply terraform plan to revert infrastructure to previous state",
                    script_type="bash",
                    script_content=templates.get("cloud_rollback", {}).get("revert_terraform", "terraform apply -target={resource_name} {rollback_plan_file}"),
                    estimated_duration_minutes=15,
                    dependencies=[],
                    validation_commands=["terraform plan -detailed-exitcode"],
                    success_criteria=["Infrastructure matches previous state", "No planned changes"],
                    failure_escalation="Manual infrastructure review required",
                    rollback_order=1
                ),
                RollbackStep(
                    step_id=f"rb_infra_{phase_index}_02",
                    name="Restore DNS configuration",
                    description="Revert DNS changes to point back to original infrastructure",
                    script_type="bash",
                    script_content=templates.get("cloud_rollback", {}).get("restore_dns", "aws route53 change-resource-record-sets --hosted-zone-id {zone_id} --change-batch file://{rollback_dns_changes}"),
                    estimated_duration_minutes=10,
                    dependencies=[f"rb_infra_{phase_index}_01"],
                    validation_commands=["nslookup {domain_name}"],
                    success_criteria=["DNS resolves to original endpoints"],
                    failure_escalation="Contact DNS administrator",
                    rollback_order=2
                )
            ])
        
        # Add generic validation step for all migration types
        steps.append(
            RollbackStep(
                step_id=f"rb_validate_{phase_index}_final",
                name="Validate rollback completion",
                description=f"Comprehensive validation that {phase_name} rollback completed successfully",
                script_type="manual",
                script_content="Execute validation checklist for this phase",
                estimated_duration_minutes=10,
                dependencies=[step.step_id for step in steps],
                validation_commands=self.validation_templates.get(migration_type, []),
                success_criteria=[f"{phase_name} fully rolled back", "All validation checks pass"],
                failure_escalation=f"Investigate {phase_name} rollback failures",
                rollback_order=99
            )
        )
        
        return steps
