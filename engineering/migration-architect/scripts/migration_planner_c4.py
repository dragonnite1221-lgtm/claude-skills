# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from migration_planner_base import *  # noqa: F403,E402
from migration_planner_p0 import MigrationPlan  # noqa: F401,E501


class MigrationPlannerMixin4:
    def generate_plan(self, spec: Dict[str, Any]) -> MigrationPlan:
        """Generate complete migration plan from specification"""
        migration_id = hashlib.md5(json.dumps(spec, sort_keys=True).encode()).hexdigest()[:12]
        complexity = self._calculate_complexity(spec)
        phases = self._generate_phases(spec)
        risks = self._assess_risks(spec)
        total_duration = sum(phase.duration_hours for phase in phases)
        rollback_plan = self._generate_rollback_plan(phases)
        
        success_criteria = [
            "All data successfully migrated with 100% integrity",
            "System performance meets or exceeds baseline",
            "All business processes functioning normally",
            "No critical security vulnerabilities introduced",
            "Stakeholder acceptance criteria met",
            "Documentation and runbooks updated"
        ]
        
        stakeholders = [
            "Business Owner",
            "Technical Lead",
            "DevOps Team",
            "QA Team", 
            "Security Team",
            "End Users"
        ]
        
        return MigrationPlan(
            migration_id=migration_id,
            source_system=spec.get("source", "Unknown"),
            target_system=spec.get("target", "Unknown"),
            migration_type=spec.get("type", "Unknown"),
            complexity=complexity,
            estimated_duration_hours=total_duration,
            phases=phases,
            risks=risks,
            success_criteria=success_criteria,
            rollback_plan=rollback_plan,
            stakeholders=stakeholders,
            created_at=datetime.datetime.now().isoformat()
        )
