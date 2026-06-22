# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from launch_checklist_base import *  # noqa: F403,E402


class LaunchChecklistGeneratorMixin2:
    def plan_seasonal_campaigns(
        self,
        app_category: str,
        current_month: int = None
    ) -> Dict[str, Any]:
        """
        Identify seasonal opportunities for ASO campaigns.

        Args:
            app_category: App category
            current_month: Current month (1-12), defaults to current

        Returns:
            Seasonal campaign opportunities
        """
        if not current_month:
            current_month = datetime.now().month

        # Identify relevant seasonal events
        seasonal_opportunities = self._identify_seasonal_opportunities(
            app_category,
            current_month
        )

        # Generate campaign ideas
        campaigns = [
            self._generate_seasonal_campaign(opportunity)
            for opportunity in seasonal_opportunities
        ]

        return {
            'current_month': current_month,
            'category': app_category,
            'seasonal_opportunities': seasonal_opportunities,
            'campaign_ideas': campaigns,
            'implementation_timeline': self._create_seasonal_timeline(campaigns)
        }
    def _generate_apple_checklist(self, app_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate Apple App Store specific checklist."""
        return [
            {
                'category': 'App Store Connect Setup',
                'items': [
                    {'task': 'App Store Connect account created', 'status': 'pending'},
                    {'task': 'App bundle ID registered', 'status': 'pending'},
                    {'task': 'App Privacy declarations completed', 'status': 'pending'},
                    {'task': 'Age rating questionnaire completed', 'status': 'pending'}
                ]
            },
            {
                'category': 'Metadata (Apple)',
                'items': [
                    {'task': 'App title (30 chars max)', 'status': 'pending'},
                    {'task': 'Subtitle (30 chars max)', 'status': 'pending'},
                    {'task': 'Promotional text (170 chars max)', 'status': 'pending'},
                    {'task': 'Description (4000 chars max)', 'status': 'pending'},
                    {'task': 'Keywords (100 chars, comma-separated)', 'status': 'pending'},
                    {'task': 'Category selection (primary + secondary)', 'status': 'pending'}
                ]
            },
            {
                'category': 'Visual Assets (Apple)',
                'items': [
                    {'task': 'App icon (1024x1024px)', 'status': 'pending'},
                    {'task': 'Screenshots (iPhone 6.7" required)', 'status': 'pending'},
                    {'task': 'Screenshots (iPhone 5.5" required)', 'status': 'pending'},
                    {'task': 'Screenshots (iPad Pro 12.9" if iPad app)', 'status': 'pending'},
                    {'task': 'App preview video (optional but recommended)', 'status': 'pending'}
                ]
            },
            {
                'category': 'Technical Requirements (Apple)',
                'items': [
                    {'task': 'Build uploaded to App Store Connect', 'status': 'pending'},
                    {'task': 'TestFlight testing completed', 'status': 'pending'},
                    {'task': 'App tested on required iOS versions', 'status': 'pending'},
                    {'task': 'Crash-free rate > 99%', 'status': 'pending'},
                    {'task': 'All links in app/metadata working', 'status': 'pending'}
                ]
            },
            {
                'category': 'Legal & Privacy (Apple)',
                'items': [
                    {'task': 'Privacy Policy URL provided', 'status': 'pending'},
                    {'task': 'Terms of Service URL (if applicable)', 'status': 'pending'},
                    {'task': 'Data collection declarations accurate', 'status': 'pending'},
                    {'task': 'Third-party SDKs disclosed', 'status': 'pending'}
                ]
            }
        ]
