# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from launch_checklist_base import *  # noqa: F403,E402


class LaunchChecklistGeneratorMixin4:
    def _generate_launch_timeline(self, launch_date: str) -> List[Dict[str, Any]]:
        """Generate timeline with milestones leading to launch."""
        launch_dt = datetime.strptime(launch_date, '%Y-%m-%d')

        milestones = [
            {
                'date': (launch_dt - timedelta(days=90)).strftime('%Y-%m-%d'),
                'milestone': '90 days before: Complete keyword research and competitor analysis'
            },
            {
                'date': (launch_dt - timedelta(days=60)).strftime('%Y-%m-%d'),
                'milestone': '60 days before: Finalize metadata and visual assets'
            },
            {
                'date': (launch_dt - timedelta(days=45)).strftime('%Y-%m-%d'),
                'milestone': '45 days before: Begin beta testing program'
            },
            {
                'date': (launch_dt - timedelta(days=30)).strftime('%Y-%m-%d'),
                'milestone': '30 days before: Submit app for review (Apple typically takes 1-2 days, Google instant)'
            },
            {
                'date': (launch_dt - timedelta(days=14)).strftime('%Y-%m-%d'),
                'milestone': '14 days before: Prepare launch marketing materials'
            },
            {
                'date': (launch_dt - timedelta(days=7)).strftime('%Y-%m-%d'),
                'milestone': '7 days before: Set up analytics and monitoring'
            },
            {
                'date': launch_dt.strftime('%Y-%m-%d'),
                'milestone': 'Launch Day: Release app and execute marketing plan'
            },
            {
                'date': (launch_dt + timedelta(days=7)).strftime('%Y-%m-%d'),
                'milestone': '7 days after: Monitor metrics, respond to reviews, address critical issues'
            },
            {
                'date': (launch_dt + timedelta(days=30)).strftime('%Y-%m-%d'),
                'milestone': '30 days after: Analyze launch metrics, plan first update'
            }
        ]

        return milestones
    def _calculate_checklist_summary(self, checklists: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Calculate completion summary."""
        total_items = 0
        completed_items = 0

        for platform, categories in checklists.items():
            for category in categories:
                for item in category['items']:
                    total_items += 1
                    if item['status'] == 'completed':
                        completed_items += 1

        completion_percentage = (completed_items / total_items * 100) if total_items > 0 else 0

        return {
            'total_items': total_items,
            'completed_items': completed_items,
            'pending_items': total_items - completed_items,
            'completion_percentage': round(completion_percentage, 1),
            'is_ready_to_launch': completion_percentage == 100
        }
    def _validate_apple_compliance(
        self,
        app_data: Dict[str, Any],
        validation_results: Dict[str, Any]
    ) -> None:
        """Validate Apple App Store compliance."""
        # Check for required fields
        if not app_data.get('privacy_policy_url'):
            validation_results['errors'].append("Privacy Policy URL is required")

        if not app_data.get('app_icon'):
            validation_results['errors'].append("App icon (1024x1024px) is required")

        # Check metadata character limits
        title = app_data.get('title', '')
        if len(title) > 30:
            validation_results['errors'].append(f"Title exceeds 30 characters ({len(title)})")

        # Warnings for best practices
        subtitle = app_data.get('subtitle', '')
        if not subtitle:
            validation_results['warnings'].append("Subtitle is empty - consider adding for better discoverability")

        keywords = app_data.get('keywords', '')
        if len(keywords) < 80:
            validation_results['warnings'].append(
                f"Keywords field underutilized ({len(keywords)}/100 chars) - add more keywords"
            )
