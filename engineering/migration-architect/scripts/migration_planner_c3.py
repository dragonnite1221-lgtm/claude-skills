# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from migration_planner_base import *  # noqa: F403,E402
from migration_planner_p0 import MigrationPhase, RiskItem  # noqa: F401,E501


class MigrationPlannerMixin3:
    def _assess_risks(self, spec: Dict[str, Any]) -> List[RiskItem]:
        """Generate risk assessment for migration"""
        migration_type = spec.get("type")
        base_risks = self.risk_templates.get(migration_type, [])
        
        # Add specification-specific risks
        additional_risks = []
        constraints = spec.get("constraints", {})
        
        if constraints.get("max_downtime_minutes", 480) < 60:
            additional_risks.append(
                RiskItem("business", "Zero-downtime requirement increases complexity", "high", "medium", "high",
                        "Implement blue-green deployment or rolling update strategy", "DevOps Team")
            )
        
        if constraints.get("data_volume_gb", 0) > 5000:
            additional_risks.append(
                RiskItem("technical", "Large data volumes may cause extended migration time", "high", "medium", "medium",
                        "Implement parallel processing and progress monitoring", "Data Team")
            )
        
        compliance_reqs = constraints.get("compliance_requirements", [])
        if compliance_reqs:
            additional_risks.append(
                RiskItem("compliance", "Regulatory compliance requirements", "medium", "high", "high",
                        "Ensure all compliance checks are integrated into migration process", "Compliance Team")
            )
        
        return base_risks + additional_risks
    def _generate_rollback_plan(self, phases: List[MigrationPhase]) -> Dict[str, Any]:
        """Generate comprehensive rollback plan"""
        rollback_phases = []
        
        for phase in reversed(phases):
            rollback_phase = {
                "phase": phase.name,
                "rollback_actions": [
                    f"Revert {phase.name} changes",
                    f"Restore pre-{phase.name} state",
                    f"Validate {phase.name} rollback success"
                ],
                "validation_criteria": [
                    f"System restored to pre-{phase.name} state",
                    f"All {phase.name} changes successfully reverted",
                    "System functionality confirmed"
                ],
                "estimated_time_minutes": phase.duration_hours * 15  # 25% of original phase time
            }
            rollback_phases.append(rollback_phase)
        
        return {
            "rollback_phases": rollback_phases,
            "rollback_triggers": [
                "Critical system failure",
                "Data corruption detected",
                "Migration timeline exceeded by > 50%",
                "Business-critical functionality unavailable",
                "Security breach detected",
                "Stakeholder decision to abort"
            ],
            "rollback_decision_matrix": {
                "low_severity": "Continue with monitoring",
                "medium_severity": "Assess and decide within 15 minutes",
                "high_severity": "Immediate rollback initiation",
                "critical_severity": "Emergency rollback - all hands"
            },
            "rollback_contacts": [
                "Migration Lead",
                "Technical Lead", 
                "Business Owner",
                "On-call Engineer"
            ]
        }
