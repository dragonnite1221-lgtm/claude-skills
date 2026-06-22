# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from migration_planner_base import *  # noqa: F403,E402
from migration_planner_p0 import MigrationPhase  # noqa: F401,E501


class MigrationPlannerMixin2:
    def _create_phase(self, phase_name: str, duration: int, complexity: str, 
                     phase_index: int, all_phases: List[str]) -> MigrationPhase:
        """Create a detailed migration phase"""
        phase_templates = {
            "preparation": {
                "description": "Prepare systems and teams for migration",
                "tasks": [
                    "Backup source system",
                    "Set up monitoring and alerting",
                    "Prepare rollback procedures",
                    "Communicate migration timeline",
                    "Validate prerequisites"
                ],
                "validation_criteria": [
                    "All backups completed successfully",
                    "Monitoring systems operational",
                    "Team members briefed and ready",
                    "Rollback procedures tested"
                ],
                "risk_level": "medium"
            },
            "assessment": {
                "description": "Assess current state and migration requirements",
                "tasks": [
                    "Inventory existing systems and dependencies",
                    "Analyze data volumes and complexity",
                    "Identify integration points",
                    "Document current architecture",
                    "Create migration mapping"
                ],
                "validation_criteria": [
                    "Complete system inventory documented",
                    "Dependencies mapped and validated",
                    "Migration scope clearly defined",
                    "Resource requirements identified"
                ],
                "risk_level": "low"
            },
            "migration": {
                "description": "Execute core migration processes",
                "tasks": [
                    "Begin data/service migration",
                    "Monitor migration progress",
                    "Validate data consistency",
                    "Handle migration errors",
                    "Update configuration"
                ],
                "validation_criteria": [
                    "Migration progress within expected parameters",
                    "Data consistency checks passing",
                    "Error rates within acceptable limits",
                    "Performance metrics stable"
                ],
                "risk_level": "high"
            },
            "validation": {
                "description": "Validate migration success and system health",
                "tasks": [
                    "Execute comprehensive testing",
                    "Validate business processes",
                    "Check system performance",
                    "Verify data integrity",
                    "Confirm security controls"
                ],
                "validation_criteria": [
                    "All critical tests passing",
                    "Performance within acceptable range",
                    "Security controls functioning",
                    "Business processes operational"
                ],
                "risk_level": "medium"
            },
            "cutover": {
                "description": "Switch production traffic to new system",
                "tasks": [
                    "Update DNS/load balancer configuration",
                    "Redirect production traffic",
                    "Monitor system performance",
                    "Validate end-user experience",
                    "Confirm business operations"
                ],
                "validation_criteria": [
                    "Traffic successfully redirected",
                    "System performance stable",
                    "User experience satisfactory",
                    "Business operations normal"
                ],
                "risk_level": "critical"
            }
        }
        
        template = phase_templates.get(phase_name, {
            "description": f"Execute {phase_name} phase",
            "tasks": [f"Complete {phase_name} activities"],
            "validation_criteria": [f"{phase_name.title()} phase completed successfully"],
            "risk_level": "medium"
        })
        
        dependencies = []
        if phase_index > 0:
            dependencies.append(all_phases[phase_index - 1])
        
        rollback_triggers = [
            "Critical system failure",
            "Data corruption detected",
            "Performance degradation > 50%",
            "Business process failure"
        ]
        
        resources_required = [
            "Technical team availability",
            "System access and permissions",
            "Monitoring and alerting systems",
            "Communication channels"
        ]
        
        return MigrationPhase(
            name=phase_name,
            description=template["description"],
            duration_hours=duration,
            dependencies=dependencies,
            validation_criteria=template["validation_criteria"],
            rollback_triggers=rollback_triggers,
            tasks=template["tasks"],
            risk_level=template["risk_level"],
            resources_required=resources_required
        )
