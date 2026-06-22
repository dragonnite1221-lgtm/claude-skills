# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from launch_checklist_base import *  # noqa: F403,E402


class LaunchChecklistGeneratorMixin3:
    def _generate_google_checklist(self, app_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate Google Play Store specific checklist."""
        return [
            {
                'category': 'Play Console Setup',
                'items': [
                    {'task': 'Google Play Console account created', 'status': 'pending'},
                    {'task': 'Developer profile completed', 'status': 'pending'},
                    {'task': 'Payment merchant account linked (if paid app)', 'status': 'pending'},
                    {'task': 'Content rating questionnaire completed', 'status': 'pending'}
                ]
            },
            {
                'category': 'Metadata (Google)',
                'items': [
                    {'task': 'App title (50 chars max)', 'status': 'pending'},
                    {'task': 'Short description (80 chars max)', 'status': 'pending'},
                    {'task': 'Full description (4000 chars max)', 'status': 'pending'},
                    {'task': 'Category selection', 'status': 'pending'},
                    {'task': 'Tags (up to 5)', 'status': 'pending'}
                ]
            },
            {
                'category': 'Visual Assets (Google)',
                'items': [
                    {'task': 'App icon (512x512px)', 'status': 'pending'},
                    {'task': 'Feature graphic (1024x500px)', 'status': 'pending'},
                    {'task': 'Screenshots (2-8 required, phone)', 'status': 'pending'},
                    {'task': 'Screenshots (tablet, if applicable)', 'status': 'pending'},
                    {'task': 'Promo video (YouTube link, optional)', 'status': 'pending'}
                ]
            },
            {
                'category': 'Technical Requirements (Google)',
                'items': [
                    {'task': 'APK/AAB uploaded to Play Console', 'status': 'pending'},
                    {'task': 'Internal testing completed', 'status': 'pending'},
                    {'task': 'App tested on required Android versions', 'status': 'pending'},
                    {'task': 'Target API level meets requirements', 'status': 'pending'},
                    {'task': 'All permissions justified', 'status': 'pending'}
                ]
            },
            {
                'category': 'Legal & Privacy (Google)',
                'items': [
                    {'task': 'Privacy Policy URL provided', 'status': 'pending'},
                    {'task': 'Data safety section completed', 'status': 'pending'},
                    {'task': 'Ads disclosure (if applicable)', 'status': 'pending'},
                    {'task': 'In-app purchase disclosure (if applicable)', 'status': 'pending'}
                ]
            }
        ]
    def _generate_universal_checklist(self, app_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate universal (both platforms) checklist."""
        return [
            {
                'category': 'Pre-Launch Marketing',
                'items': [
                    {'task': 'Landing page created', 'status': 'pending'},
                    {'task': 'Social media accounts setup', 'status': 'pending'},
                    {'task': 'Press kit prepared', 'status': 'pending'},
                    {'task': 'Beta tester feedback collected', 'status': 'pending'},
                    {'task': 'Launch announcement drafted', 'status': 'pending'}
                ]
            },
            {
                'category': 'ASO Preparation',
                'items': [
                    {'task': 'Keyword research completed', 'status': 'pending'},
                    {'task': 'Competitor analysis done', 'status': 'pending'},
                    {'task': 'A/B test plan created for post-launch', 'status': 'pending'},
                    {'task': 'Analytics tracking configured', 'status': 'pending'}
                ]
            },
            {
                'category': 'Quality Assurance',
                'items': [
                    {'task': 'All core features tested', 'status': 'pending'},
                    {'task': 'User flows validated', 'status': 'pending'},
                    {'task': 'Performance testing completed', 'status': 'pending'},
                    {'task': 'Accessibility features tested', 'status': 'pending'},
                    {'task': 'Security audit completed', 'status': 'pending'}
                ]
            },
            {
                'category': 'Support Infrastructure',
                'items': [
                    {'task': 'Support email/system setup', 'status': 'pending'},
                    {'task': 'FAQ page created', 'status': 'pending'},
                    {'task': 'Documentation for users prepared', 'status': 'pending'},
                    {'task': 'Team trained on handling reviews', 'status': 'pending'}
                ]
            }
        ]
