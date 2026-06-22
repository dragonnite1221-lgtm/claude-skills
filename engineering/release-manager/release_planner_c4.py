# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from release_planner_base import *  # noqa: F403,E402
from release_planner_p0 import RiskLevel  # noqa: F401,E501


class ReleasePlannerMixin4:
    def _check_pm_approvals(self) -> bool:
        """Check PM approvals."""
        return all(f.pm_approved for f in self.features if f.risk_level != RiskLevel.LOW)
    def _check_qa_approvals(self) -> bool:
        """Check QA approvals.""" 
        return all(f.qa_approved for f in self.features)
    def _check_security_approvals(self) -> bool:
        """Check security approvals."""
        high_risk_features = [f for f in self.features if f.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]]
        return all(f.security_approved for f in high_risk_features)
    def generate_communication_plan(self) -> Dict:
        """Generate stakeholder communication plan."""
        plan = {
            'internal_notifications': [],
            'external_notifications': [],
            'timeline': [],
            'channels': {},
            'templates': {}
        }
        
        # Group stakeholders by type
        internal_stakeholders = [s for s in self.stakeholders if s.role in 
                               ['developer', 'qa', 'pm', 'devops', 'security']]
        external_stakeholders = [s for s in self.stakeholders if s.role in 
                               ['customer', 'partner', 'support']]
        
        # Internal notifications
        for stakeholder in internal_stakeholders:
            plan['internal_notifications'].append({
                'recipient': stakeholder.name,
                'role': stakeholder.role,
                'method': stakeholder.notification_type,
                'content_type': 'technical_details',
                'timing': 'T-24h and T-0'
            })
        
        # External notifications
        for stakeholder in external_stakeholders:
            plan['external_notifications'].append({
                'recipient': stakeholder.name,
                'role': stakeholder.role,
                'method': stakeholder.notification_type,
                'content_type': 'user_facing_changes',
                'timing': 'T-48h and T+1h'
            })
        
        # Communication timeline
        if self.target_date:
            timeline_items = [
                (timedelta(days=-2), 'Send pre-release notification to external stakeholders'),
                (timedelta(days=-1), 'Send deployment notification to internal teams'),
                (timedelta(hours=-2), 'Final go/no-go decision'),
                (timedelta(hours=0), 'Begin deployment'),
                (timedelta(hours=1), 'Post-deployment status update'),
                (timedelta(hours=24), 'Post-release summary')
            ]
            
            for delta, description in timeline_items:
                notification_time = self.target_date + delta
                plan['timeline'].append({
                    'time': notification_time.isoformat(),
                    'description': description,
                    'recipients': 'all' if 'all' in description.lower() else 'internal'
                })
        
        # Communication channels
        channels = {}
        for stakeholder in self.stakeholders:
            if stakeholder.notification_type not in channels:
                channels[stakeholder.notification_type] = []
            channels[stakeholder.notification_type].append(stakeholder.contact)
        plan['channels'] = channels
        
        # Message templates
        plan['templates'] = self._generate_message_templates()
        
        return plan
