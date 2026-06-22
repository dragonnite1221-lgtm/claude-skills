# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from rollback_generator_base import *  # noqa: F403,E402


class RollbackGeneratorMixin0:
    """Main rollback generator class"""
    def __init__(self):
        self.rollback_templates = self._load_rollback_templates()
        self.validation_templates = self._load_validation_templates()
        self.communication_templates = self._load_communication_templates()
    def _load_rollback_templates(self) -> Dict[str, Any]:
        """Load rollback script templates for different migration types"""
        return {
            "database": {
                "schema_rollback": {
                    "drop_table": "DROP TABLE IF EXISTS {table_name};",
                    "drop_column": "ALTER TABLE {table_name} DROP COLUMN IF EXISTS {column_name};",
                    "restore_column": "ALTER TABLE {table_name} ADD COLUMN {column_definition};",
                    "revert_type": "ALTER TABLE {table_name} ALTER COLUMN {column_name} TYPE {original_type};",
                    "drop_constraint": "ALTER TABLE {table_name} DROP CONSTRAINT {constraint_name};",
                    "add_constraint": "ALTER TABLE {table_name} ADD CONSTRAINT {constraint_name} {constraint_definition};"
                },
                "data_rollback": {
                    "restore_backup": "pg_restore -d {database_name} -c {backup_file}",
                    "point_in_time_recovery": "SELECT pg_create_restore_point('pre_migration_{timestamp}');",
                    "delete_migrated_data": "DELETE FROM {table_name} WHERE migration_batch_id = '{batch_id}';",
                    "restore_original_values": "UPDATE {table_name} SET {column_name} = backup_{column_name} WHERE migration_flag = true;"
                }
            },
            "service": {
                "deployment_rollback": {
                    "rollback_blue_green": "kubectl patch service {service_name} -p '{\"spec\":{\"selector\":{\"version\":\"blue\"}}}'",
                    "rollback_canary": "kubectl scale deployment {service_name}-canary --replicas=0",
                    "restore_previous_version": "kubectl rollout undo deployment/{service_name} --to-revision={revision_number}",
                    "update_load_balancer": "aws elbv2 modify-rule --rule-arn {rule_arn} --actions Type=forward,TargetGroupArn={original_target_group}"
                },
                "configuration_rollback": {
                    "restore_config_map": "kubectl apply -f {original_config_file}",
                    "revert_feature_flags": "curl -X PUT {feature_flag_api}/flags/{flag_name} -d '{\"enabled\": false}'",
                    "restore_environment_vars": "kubectl set env deployment/{deployment_name} {env_var_name}={original_value}"
                }
            },
            "infrastructure": {
                "cloud_rollback": {
                    "revert_terraform": "terraform apply -target={resource_name} {rollback_plan_file}",
                    "restore_dns": "aws route53 change-resource-record-sets --hosted-zone-id {zone_id} --change-batch file://{rollback_dns_changes}",
                    "rollback_security_groups": "aws ec2 authorize-security-group-ingress --group-id {group_id} --protocol {protocol} --port {port} --cidr {cidr}",
                    "restore_iam_policies": "aws iam put-role-policy --role-name {role_name} --policy-name {policy_name} --policy-document file://{original_policy}"
                },
                "network_rollback": {
                    "restore_routing": "aws ec2 replace-route --route-table-id {route_table_id} --destination-cidr-block {cidr} --gateway-id {original_gateway}",
                    "revert_load_balancer": "aws elbv2 modify-load-balancer --load-balancer-arn {lb_arn} --scheme {original_scheme}",
                    "restore_firewall_rules": "aws ec2 revoke-security-group-ingress --group-id {group_id} --protocol {protocol} --port {port} --source-group {source_group}"
                }
            }
        }
    def _load_validation_templates(self) -> Dict[str, List[str]]:
        """Load validation command templates"""
        return {
            "database": [
                "SELECT COUNT(*) FROM {table_name};",
                "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = '{table_name}';",
                "SELECT COUNT(*) FROM information_schema.columns WHERE table_name = '{table_name}' AND column_name = '{column_name}';",
                "SELECT COUNT(DISTINCT {primary_key}) FROM {table_name};",
                "SELECT MAX({timestamp_column}) FROM {table_name};"
            ],
            "service": [
                "curl -f {health_check_url}",
                "kubectl get pods -l app={service_name} --field-selector=status.phase=Running",
                "kubectl logs deployment/{service_name} --tail=100 | grep -i error",
                "curl -f {service_endpoint}/api/v1/status"
            ],
            "infrastructure": [
                "aws ec2 describe-instances --instance-ids {instance_id} --query 'Reservations[*].Instances[*].State.Name'",
                "nslookup {domain_name}",
                "curl -I {load_balancer_url}",
                "aws elbv2 describe-target-health --target-group-arn {target_group_arn}"
            ]
        }
