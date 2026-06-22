# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from release_planner_base import *  # noqa: F403,E402
from release_planner_p0 import ComponentStatus, Feature, QualityGate, RiskLevel, RollbackStep, Stakeholder  # noqa: F401,E501


class ReleasePlannerMixin0:
    """Main release planning and assessment logic."""
    def __init__(self):
        self.release_name: str = ""
        self.version: str = ""
        self.target_date: Optional[datetime] = None
        self.features: List[Feature] = []
        self.quality_gates: List[QualityGate] = []
        self.stakeholders: List[Stakeholder] = []
        self.rollback_steps: List[RollbackStep] = []
        
        # Configuration
        self.min_test_coverage = 80.0
        self.required_approvals = ['pm_approved', 'qa_approved']
        self.high_risk_approval_requirements = ['pm_approved', 'qa_approved', 'security_approved']
    def load_release_plan(self, plan_data: Union[str, Dict]):
        """Load release plan from JSON."""
        if isinstance(plan_data, str):
            data = json.loads(plan_data)
        else:
            data = plan_data
        
        self.release_name = data.get('release_name', 'Unnamed Release')
        self.version = data.get('version', '1.0.0')
        
        if 'target_date' in data:
            self.target_date = datetime.fromisoformat(data['target_date'].replace('Z', '+00:00'))
        
        # Load features
        self.features = []
        for feature_data in data.get('features', []):
            try:
                status = ComponentStatus(feature_data.get('status', 'pending'))
                risk_level = RiskLevel(feature_data.get('risk_level', 'medium'))
                
                feature = Feature(
                    id=feature_data['id'],
                    title=feature_data['title'],
                    description=feature_data.get('description', ''),
                    type=feature_data.get('type', 'feature'),
                    assignee=feature_data.get('assignee', ''),
                    status=status,
                    pull_request_url=feature_data.get('pull_request_url'),
                    issue_url=feature_data.get('issue_url'),
                    risk_level=risk_level,
                    test_coverage_required=feature_data.get('test_coverage_required', 80.0),
                    test_coverage_actual=feature_data.get('test_coverage_actual'),
                    requires_migration=feature_data.get('requires_migration', False),
                    migration_complexity=feature_data.get('migration_complexity', 'simple'),
                    breaking_changes=feature_data.get('breaking_changes', []),
                    dependencies=feature_data.get('dependencies', []),
                    qa_approved=feature_data.get('qa_approved', False),
                    security_approved=feature_data.get('security_approved', False),
                    pm_approved=feature_data.get('pm_approved', False)
                )
                self.features.append(feature)
            except Exception as e:
                print(f"Warning: Error parsing feature {feature_data.get('id', 'unknown')}: {e}", 
                      file=sys.stderr)
        
        # Load quality gates
        self.quality_gates = []
        for gate_data in data.get('quality_gates', []):
            try:
                status = ComponentStatus(gate_data.get('status', 'pending'))
                gate = QualityGate(
                    name=gate_data['name'],
                    required=gate_data.get('required', True),
                    status=status,
                    details=gate_data.get('details'),
                    threshold=gate_data.get('threshold'),
                    actual_value=gate_data.get('actual_value')
                )
                self.quality_gates.append(gate)
            except Exception as e:
                print(f"Warning: Error parsing quality gate {gate_data.get('name', 'unknown')}: {e}", 
                      file=sys.stderr)
        
        # Load stakeholders
        self.stakeholders = []
        for stakeholder_data in data.get('stakeholders', []):
            stakeholder = Stakeholder(
                name=stakeholder_data['name'],
                role=stakeholder_data['role'],
                contact=stakeholder_data['contact'],
                notification_type=stakeholder_data.get('notification_type', 'email'),
                critical_path=stakeholder_data.get('critical_path', False)
            )
            self.stakeholders.append(stakeholder)
        
        # Load or generate default quality gates if none provided
        if not self.quality_gates:
            self._generate_default_quality_gates()
        
        # Load or generate default rollback steps
        if 'rollback_steps' in data:
            self.rollback_steps = []
            for step_data in data['rollback_steps']:
                risk_level = RiskLevel(step_data.get('risk_level', 'low'))
                step = RollbackStep(
                    order=step_data['order'],
                    description=step_data['description'],
                    command=step_data.get('command'),
                    estimated_time=step_data.get('estimated_time', '5 minutes'),
                    risk_level=risk_level,
                    verification=step_data.get('verification', '')
                )
                self.rollback_steps.append(step)
        else:
            self._generate_default_rollback_steps()
