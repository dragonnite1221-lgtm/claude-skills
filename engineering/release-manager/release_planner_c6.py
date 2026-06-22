# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from release_planner_base import *  # noqa: F403,E402
from release_planner_p0 import RiskLevel  # noqa: F401,E501


class ReleasePlannerMixin6:
    def generate_rollback_runbook(self) -> Dict:
        """Generate detailed rollback runbook."""
        runbook = {
            'overview': {
                'purpose': f'Emergency rollback procedure for {self.release_name} v{self.version}',
                'triggers': [
                    'Error rate spike (>2x baseline for >15 minutes)',
                    'Critical functionality failure',
                    'Security incident',
                    'Data corruption detected',
                    'Performance degradation (>50% latency increase)',
                    'Manual decision by incident commander'
                ],
                'decision_makers': ['On-call Engineer', 'Engineering Lead', 'Incident Commander'],
                'estimated_total_time': self._calculate_rollback_time()
            },
            'prerequisites': [
                'Confirm rollback is necessary (check with incident commander)',
                'Notify stakeholders of rollback decision', 
                'Ensure database backups are available',
                'Verify monitoring systems are operational',
                'Have communication channels ready'
            ],
            'steps': [],
            'verification': {
                'health_checks': [
                    'Application responds to health endpoint',
                    'Database connectivity confirmed',
                    'Authentication system functional',
                    'Core user workflows working',
                    'Error rates back to baseline',
                    'Performance metrics within normal range'
                ],
                'rollback_confirmation': [
                    'Previous version fully deployed',
                    'Database in consistent state',
                    'All services communicating properly',
                    'Monitoring shows stable metrics',
                    'Sample user workflows tested'
                ]
            },
            'post_rollback': [
                'Update status page with resolution',
                'Notify all stakeholders of successful rollback',
                'Schedule post-incident review',
                'Document issues encountered during rollback',
                'Plan investigation of root cause',
                'Determine timeline for next release attempt'
            ],
            'emergency_contacts': []
        }
        
        # Convert rollback steps to detailed format
        for step in sorted(self.rollback_steps, key=lambda x: x.order):
            step_data = {
                'order': step.order,
                'title': step.description,
                'estimated_time': step.estimated_time,
                'risk_level': step.risk_level.value,
                'instructions': step.description,
                'command': step.command,
                'verification': step.verification,
                'rollback_possible': step.risk_level != RiskLevel.CRITICAL
            }
            runbook['steps'].append(step_data)
        
        # Add emergency contacts
        critical_stakeholders = [s for s in self.stakeholders if s.critical_path]
        for stakeholder in critical_stakeholders:
            runbook['emergency_contacts'].append({
                'name': stakeholder.name,
                'role': stakeholder.role,
                'contact': stakeholder.contact,
                'method': stakeholder.notification_type
            })
        
        return runbook
    def _calculate_rollback_time(self) -> str:
        """Calculate estimated total rollback time."""
        total_minutes = 0
        for step in self.rollback_steps:
            # Parse time estimates like "5 minutes", "30 seconds", "1 hour"
            time_str = step.estimated_time.lower()
            if 'minute' in time_str:
                minutes = int(re.search(r'(\d+)', time_str).group(1))
                total_minutes += minutes
            elif 'hour' in time_str:
                hours = int(re.search(r'(\d+)', time_str).group(1))
                total_minutes += hours * 60
            elif 'second' in time_str:
                # Round up seconds to minutes
                total_minutes += 1
        
        if total_minutes < 60:
            return f"{total_minutes} minutes"
        else:
            hours = total_minutes // 60
            minutes = total_minutes % 60
            return f"{hours}h {minutes}m"
