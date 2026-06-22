# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from architecture_designer_base import *  # noqa: F403,E402


class ArchitectureDesignerMixin1:
    def _serverless_web_architecture(self) -> Dict[str, Any]:
        """Serverless web application pattern using Cloud Run."""
        return {
            'pattern_name': 'Serverless Web Application',
            'description': 'Fully serverless architecture with Cloud Run and Firestore',
            'use_case': 'SaaS platforms, low to medium traffic websites, MVPs',
            'services': {
                'frontend': {
                    'service': 'Cloud Storage + Cloud CDN',
                    'purpose': 'Static website hosting with global CDN',
                    'configuration': {
                        'bucket': 'Website bucket with public access',
                        'cdn': 'Cloud CDN with custom domain and HTTPS',
                        'caching': 'Cache-Control headers, edge caching'
                    }
                },
                'api': {
                    'service': 'Cloud Run',
                    'purpose': 'Containerized API backend with auto-scaling',
                    'configuration': {
                        'cpu': '1 vCPU',
                        'memory': '512 Mi',
                        'min_instances': '0 (scale to zero)',
                        'max_instances': '10',
                        'concurrency': '80 requests per instance',
                        'timeout': '300 seconds'
                    }
                },
                'database': {
                    'service': 'Firestore',
                    'purpose': 'NoSQL document database with real-time sync',
                    'configuration': {
                        'mode': 'Native mode',
                        'location': 'Regional or multi-region',
                        'security_rules': 'Firestore security rules',
                        'backup': 'Scheduled exports to Cloud Storage'
                    }
                },
                'authentication': {
                    'service': 'Identity Platform',
                    'purpose': 'User authentication and authorization',
                    'configuration': {
                        'providers': 'Email/password, Google, Apple, OIDC',
                        'mfa': 'SMS or TOTP multi-factor authentication',
                        'token_expiration': '1 hour access, 30 days refresh'
                    }
                },
                'cicd': {
                    'service': 'Cloud Build',
                    'purpose': 'Automated build and deployment from Git',
                    'configuration': {
                        'source': 'GitHub or Cloud Source Repositories',
                        'build': 'Automatic on commit',
                        'environments': 'dev, staging, production'
                    }
                }
            },
            'estimated_cost': {
                'monthly_usd': self._calculate_serverless_cost(),
                'breakdown': {
                    'Cloud CDN': '5-20 USD',
                    'Cloud Run': '5-25 USD',
                    'Firestore': '5-30 USD',
                    'Identity Platform': '0-10 USD (free tier: 50k MAU)',
                    'Cloud Storage': '1-5 USD'
                }
            },
            'pros': [
                'No server management',
                'Auto-scaling with scale-to-zero',
                'Pay only for what you use',
                'No cold starts with min instances',
                'Container-based (no runtime restrictions)'
            ],
            'cons': [
                'Vendor lock-in to GCP',
                'Regional availability considerations',
                'Debugging distributed systems complex',
                'Firestore query limitations vs SQL'
            ],
            'scaling_characteristics': {
                'users_supported': '1k - 100k',
                'requests_per_second': '100 - 10,000',
                'scaling_method': 'Automatic (Cloud Run auto-scaling)'
            }
        }
