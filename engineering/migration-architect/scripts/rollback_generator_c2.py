# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from rollback_generator_base import *  # noqa: F403,E402
from rollback_generator_p0 import RollbackPhase, RollbackRunbook  # noqa: F401,E501


class RollbackGeneratorMixin2:
    def generate_rollback_runbook(self, migration_plan: Dict[str, Any]) -> RollbackRunbook:
        """Generate comprehensive rollback runbook from migration plan"""
        runbook_id = f"rb_{hashlib.md5(str(migration_plan).encode()).hexdigest()[:8]}"
        migration_id = migration_plan.get("migration_id", "unknown")
        migration_type = migration_plan.get("migration_type", "unknown")
        
        # Generate rollback phases (reverse order of migration phases)
        rollback_phases = self._generate_rollback_phases(migration_plan)
        
        # Generate trigger conditions
        trigger_conditions = self._generate_trigger_conditions(migration_plan)
        
        # Generate data recovery plan
        data_recovery_plan = self._generate_data_recovery_plan(migration_plan)
        
        # Generate communication templates
        communication_templates = self._generate_communication_templates(migration_plan)
        
        # Generate escalation matrix
        escalation_matrix = self._generate_escalation_matrix(migration_plan)
        
        # Generate validation checklist
        validation_checklist = self._generate_validation_checklist(migration_plan)
        
        # Generate post-rollback procedures
        post_rollback_procedures = self._generate_post_rollback_procedures(migration_plan)
        
        # Generate emergency contacts
        emergency_contacts = self._generate_emergency_contacts(migration_plan)
        
        return RollbackRunbook(
            runbook_id=runbook_id,
            migration_id=migration_id,
            created_at=datetime.datetime.now().isoformat(),
            rollback_phases=rollback_phases,
            trigger_conditions=trigger_conditions,
            data_recovery_plan=data_recovery_plan,
            communication_templates=communication_templates,
            escalation_matrix=escalation_matrix,
            validation_checklist=validation_checklist,
            post_rollback_procedures=post_rollback_procedures,
            emergency_contacts=emergency_contacts
        )
    def _generate_rollback_phases(self, migration_plan: Dict[str, Any]) -> List[RollbackPhase]:
        """Generate rollback phases from migration plan"""
        migration_phases = migration_plan.get("phases", [])
        migration_type = migration_plan.get("migration_type", "unknown")
        rollback_phases = []
        
        # Reverse the order of migration phases for rollback
        for i, phase in enumerate(reversed(migration_phases)):
            if isinstance(phase, dict):
                phase_name = phase.get("name", f"phase_{i}")
                phase_duration = phase.get("duration_hours", 2) * 60  # Convert to minutes
                phase_risk = phase.get("risk_level", "medium")
            else:
                phase_name = str(phase)
                phase_duration = 120  # Default 2 hours
                phase_risk = "medium"
            
            rollback_steps = self._generate_rollback_steps(phase_name, migration_type, i)
            
            rollback_phase = RollbackPhase(
                phase_name=f"rollback_{phase_name}",
                description=f"Rollback changes made during {phase_name} phase",
                urgency_level=self._calculate_urgency(phase_risk),
                estimated_duration_minutes=phase_duration // 2,  # Rollback typically faster
                prerequisites=self._get_rollback_prerequisites(phase_name, i),
                steps=rollback_steps,
                validation_checkpoints=self._get_validation_checkpoints(phase_name, migration_type),
                communication_requirements=self._get_communication_requirements(phase_name, phase_risk),
                risk_level=phase_risk
            )
            
            rollback_phases.append(rollback_phase)
        
        return rollback_phases
