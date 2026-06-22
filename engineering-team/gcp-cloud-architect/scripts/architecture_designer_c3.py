# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from architecture_designer_base import *  # noqa: F403,E402


class ArchitectureDesignerMixin3:
    def _serverless_mobile_backend(self) -> Dict[str, Any]:
        """Serverless mobile backend with Firebase."""
        return {
            'pattern_name': 'Serverless Mobile Backend',
            'description': 'Mobile-first backend with Firebase and Cloud Functions',
            'use_case': 'Mobile apps, real-time applications, offline-first apps',
            'services': {
                'api': {
                    'service': 'Cloud Functions (2nd gen)',
                    'purpose': 'Event-driven API handlers',
                    'configuration': {
                        'runtime': 'Node.js 20 or Python 3.12',
                        'memory': '256 MB - 1 GB',
                        'timeout': '60 seconds',
                        'concurrency': 'Up to 1000 concurrent'
                    }
                },
                'database': {
                    'service': 'Firestore',
                    'purpose': 'Real-time NoSQL database with offline sync',
                    'configuration': {
                        'mode': 'Native mode',
                        'multi_region': 'nam5 or eur3 for HA',
                        'security_rules': 'Client-side access control',
                        'indexes': 'Composite indexes for queries'
                    }
                },
                'file_storage': {
                    'service': 'Cloud Storage (Firebase)',
                    'purpose': 'User uploads (images, videos, documents)',
                    'configuration': {
                        'access': 'Firebase Security Rules',
                        'resumable_uploads': 'Enabled for large files',
                        'cdn': 'Automatic via Firebase Hosting CDN'
                    }
                },
                'authentication': {
                    'service': 'Firebase Authentication',
                    'purpose': 'User management and federation',
                    'configuration': {
                        'providers': 'Email, Google, Apple, Phone',
                        'anonymous_auth': 'Enabled for guest access',
                        'custom_claims': 'Role-based access control',
                        'multi_tenancy': 'Supported via Identity Platform'
                    }
                },
                'push_notifications': {
                    'service': 'Firebase Cloud Messaging (FCM)',
                    'purpose': 'Push notifications to mobile devices',
                    'configuration': {
                        'platforms': 'iOS (APNs), Android, Web',
                        'topics': 'Topic-based group messaging',
                        'analytics': 'Notification delivery tracking'
                    }
                },
                'analytics': {
                    'service': 'Google Analytics (Firebase)',
                    'purpose': 'User analytics and event tracking',
                    'configuration': {
                        'events': 'Custom and automatic events',
                        'audiences': 'User segmentation',
                        'bigquery_export': 'Raw event export to BigQuery'
                    }
                }
            },
            'estimated_cost': {
                'monthly_usd': 40 + (self.expected_users * 0.004),
                'breakdown': {
                    'Cloud Functions': '5-30 USD',
                    'Firestore': '10-50 USD',
                    'Cloud Storage': '5-20 USD',
                    'Identity Platform': '0-15 USD',
                    'FCM': '0 USD (free)',
                    'Analytics': '0 USD (free)'
                }
            },
            'pros': [
                'Real-time data sync built-in',
                'Offline-first support',
                'Firebase SDKs for iOS/Android/Web',
                'Free tier covers most MVPs',
                'Rapid development with Firebase console'
            ],
            'cons': [
                'Firestore query limitations',
                'Vendor lock-in to Firebase/GCP',
                'Cost scaling can be unpredictable',
                'Limited server-side control'
            ],
            'scaling_characteristics': {
                'users_supported': '1k - 1M',
                'requests_per_second': '100 - 100,000',
                'scaling_method': 'Automatic (Firebase managed)'
            }
        }
