# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from release_planner_base import *  # noqa: F403,E402


class ReleasePlannerMixin5:
    def _generate_message_templates(self) -> Dict:
        """Generate message templates for different audiences."""
        breaking_changes = [f for f in self.features if f.breaking_changes]
        new_features = [f for f in self.features if f.type == 'feature']
        bug_fixes = [f for f in self.features if f.type == 'bugfix']
        
        templates = {
            'internal_pre_release': {
                'subject': f'Release {self.version} - Pre-deployment Notification',
                'body': f"""Team,

We are preparing to deploy {self.release_name} version {self.version} on {self.target_date.strftime('%Y-%m-%d %H:%M UTC') if self.target_date else 'TBD'}.

Key Changes:
- {len(new_features)} new features
- {len(bug_fixes)} bug fixes
- {len(breaking_changes)} breaking changes

Please review the release notes and prepare for any needed support activities.

Rollback plan: Available in release documentation
On-call: Please be available during deployment window

Best regards,
Release Team"""
            },
            'external_user_notification': {
                'subject': f'Product Update - Version {self.version} Now Available',
                'body': f"""Dear Users,

We're excited to announce version {self.version} of {self.release_name} is now available!

What's New:
{chr(10).join(f"- {f.title}" for f in new_features[:5])}

Bug Fixes:
{chr(10).join(f"- {f.title}" for f in bug_fixes[:3])}

{'Important: This release includes breaking changes. Please review the migration guide.' if breaking_changes else ''}

For full release notes and migration instructions, visit our documentation.

Thank you for using our product!

The Development Team"""
            },
            'rollback_notification': {
                'subject': f'URGENT: Release {self.version} Rollback Initiated',
                'body': f"""ATTENTION: Release rollback in progress.

Release: {self.version}
Reason: [TO BE FILLED]
Rollback initiated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}
Estimated completion: [TO BE FILLED]

Current status: Rolling back to previous stable version
Impact: [TO BE FILLED]

We will provide updates every 15 minutes until rollback is complete.

Incident Commander: [TO BE FILLED]
Status page: [TO BE FILLED]"""
            }
        }
        
        return templates
