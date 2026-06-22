# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from rollback_generator_base import *  # noqa: F403,E402
from rollback_generator_p0 import RollbackTriggerCondition  # noqa: F401,E501


class RollbackGeneratorMixin4:
    def _generate_trigger_conditions(self, migration_plan: Dict[str, Any]) -> List[RollbackTriggerCondition]:
        """Generate automatic rollback trigger conditions"""
        triggers = []
        migration_type = migration_plan.get("migration_type", "unknown")
        
        # Generic triggers for all migration types
        triggers.extend([
            RollbackTriggerCondition(
                trigger_id="error_rate_spike",
                name="Error Rate Spike",
                condition="error_rate > baseline * 5 for 5 minutes",
                metric_threshold={
                    "metric": "error_rate",
                    "operator": "greater_than",
                    "value": "baseline_error_rate * 5",
                    "duration_minutes": 5
                },
                evaluation_window_minutes=5,
                auto_execute=True,
                escalation_contacts=["on_call_engineer", "migration_lead"]
            ),
            RollbackTriggerCondition(
                trigger_id="response_time_degradation",
                name="Response Time Degradation",
                condition="p95_response_time > baseline * 3 for 10 minutes",
                metric_threshold={
                    "metric": "p95_response_time",
                    "operator": "greater_than",
                    "value": "baseline_p95 * 3",
                    "duration_minutes": 10
                },
                evaluation_window_minutes=10,
                auto_execute=False,
                escalation_contacts=["performance_team", "migration_lead"]
            ),
            RollbackTriggerCondition(
                trigger_id="availability_drop",
                name="Service Availability Drop",
                condition="availability < 95% for 2 minutes",
                metric_threshold={
                    "metric": "availability",
                    "operator": "less_than",
                    "value": 0.95,
                    "duration_minutes": 2
                },
                evaluation_window_minutes=2,
                auto_execute=True,
                escalation_contacts=["sre_team", "incident_commander"]
            )
        ])
        
        # Migration-type specific triggers
        if migration_type == "database":
            triggers.extend([
                RollbackTriggerCondition(
                    trigger_id="data_integrity_failure",
                    name="Data Integrity Check Failure",
                    condition="data_validation_failures > 0",
                    metric_threshold={
                        "metric": "data_validation_failures",
                        "operator": "greater_than",
                        "value": 0,
                        "duration_minutes": 1
                    },
                    evaluation_window_minutes=1,
                    auto_execute=True,
                    escalation_contacts=["dba_team", "data_team"]
                ),
                RollbackTriggerCondition(
                    trigger_id="migration_progress_stalled",
                    name="Migration Progress Stalled",
                    condition="migration_progress unchanged for 30 minutes",
                    metric_threshold={
                        "metric": "migration_progress_rate",
                        "operator": "equals",
                        "value": 0,
                        "duration_minutes": 30
                    },
                    evaluation_window_minutes=30,
                    auto_execute=False,
                    escalation_contacts=["migration_team", "dba_team"]
                )
            ])
        
        elif migration_type == "service":
            triggers.extend([
                RollbackTriggerCondition(
                    trigger_id="cpu_utilization_spike",
                    name="CPU Utilization Spike",
                    condition="cpu_utilization > 90% for 15 minutes",
                    metric_threshold={
                        "metric": "cpu_utilization",
                        "operator": "greater_than",
                        "value": 0.90,
                        "duration_minutes": 15
                    },
                    evaluation_window_minutes=15,
                    auto_execute=False,
                    escalation_contacts=["devops_team", "infrastructure_team"]
                ),
                RollbackTriggerCondition(
                    trigger_id="memory_leak_detected",
                    name="Memory Leak Detected",
                    condition="memory_usage increasing continuously for 20 minutes",
                    metric_threshold={
                        "metric": "memory_growth_rate",
                        "operator": "greater_than",
                        "value": "1MB/minute",
                        "duration_minutes": 20
                    },
                    evaluation_window_minutes=20,
                    auto_execute=True,
                    escalation_contacts=["development_team", "sre_team"]
                )
            ])
        
        return triggers
