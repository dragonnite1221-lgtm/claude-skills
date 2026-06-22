# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from release_planner_base import *  # noqa: F403,E402
from release_planner_p0 import ComponentStatus, QualityGate, RiskLevel, RollbackStep  # noqa: F401,E501


class ReleasePlannerMixin1:
    def _generate_default_quality_gates(self):
        """Generate default quality gates."""
        default_gates = [
            {
                'name': 'Unit Test Coverage',
                'required': True,
                'threshold': self.min_test_coverage,
                'details': f'Minimum {self.min_test_coverage}% code coverage required'
            },
            {
                'name': 'Integration Tests',
                'required': True,
                'details': 'All integration tests must pass'
            },
            {
                'name': 'Security Scan',
                'required': True,
                'details': 'No high or critical security vulnerabilities'
            },
            {
                'name': 'Performance Testing',
                'required': True,
                'details': 'Performance metrics within acceptable thresholds'
            },
            {
                'name': 'Documentation Review',
                'required': True,
                'details': 'API docs and user docs updated for new features'
            },
            {
                'name': 'Dependency Audit',
                'required': True,
                'details': 'All dependencies scanned for vulnerabilities'
            }
        ]
        
        self.quality_gates = []
        for gate_data in default_gates:
            gate = QualityGate(
                name=gate_data['name'],
                required=gate_data['required'],
                status=ComponentStatus.PENDING,
                details=gate_data['details'],
                threshold=gate_data.get('threshold')
            )
            self.quality_gates.append(gate)
    def _generate_default_rollback_steps(self):
        """Generate default rollback procedure."""
        default_steps = [
            {
                'order': 1,
                'description': 'Alert on-call team and stakeholders',
                'estimated_time': '2 minutes',
                'verification': 'Confirm team is aware and responding'
            },
            {
                'order': 2,
                'description': 'Switch load balancer to previous version',
                'command': 'kubectl patch service app --patch \'{"spec": {"selector": {"version": "previous"}}}\'',
                'estimated_time': '30 seconds',
                'verification': 'Check that traffic is routing to old version'
            },
            {
                'order': 3,
                'description': 'Verify application health after rollback',
                'estimated_time': '5 minutes',
                'verification': 'Check error rates, response times, and health endpoints'
            },
            {
                'order': 4,
                'description': 'Roll back database migrations if needed',
                'command': 'python manage.py migrate app 0001',
                'estimated_time': '10 minutes',
                'risk_level': 'high',
                'verification': 'Verify data integrity and application functionality'
            },
            {
                'order': 5,
                'description': 'Update monitoring dashboards and alerts',
                'estimated_time': '5 minutes',
                'verification': 'Confirm metrics reflect rollback state'
            },
            {
                'order': 6,
                'description': 'Notify stakeholders of successful rollback',
                'estimated_time': '5 minutes',
                'verification': 'All stakeholders acknowledge rollback completion'
            }
        ]
        
        self.rollback_steps = []
        for step_data in default_steps:
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
