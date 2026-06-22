# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from architecture_designer_base import *  # noqa: F403,E402


class ArchitectureDesignerMixin2:
    def _gke_microservices_architecture(self) -> Dict[str, Any]:
        """GKE-based microservices architecture."""
        return {
            'pattern_name': 'Microservices on GKE',
            'description': 'Kubernetes-native architecture with managed services',
            'use_case': 'SaaS platforms, complex microservices, enterprise applications',
            'services': {
                'load_balancer': {
                    'service': 'Cloud Load Balancing',
                    'purpose': 'Global HTTP(S) load balancing',
                    'configuration': {
                        'type': 'External Application Load Balancer',
                        'ssl': 'Google-managed SSL certificate',
                        'health_checks': '/health endpoint, 10s interval',
                        'cdn': 'Cloud CDN enabled for static content'
                    }
                },
                'compute': {
                    'service': 'GKE Autopilot',
                    'purpose': 'Managed Kubernetes for containerized workloads',
                    'configuration': {
                        'mode': 'Autopilot (fully managed node provisioning)',
                        'scaling': 'Horizontal Pod Autoscaler',
                        'networking': 'VPC-native with Alias IPs',
                        'workload_identity': 'Enabled for secure service account binding'
                    }
                },
                'database': {
                    'service': 'Cloud SQL (PostgreSQL)',
                    'purpose': 'Managed relational database',
                    'configuration': {
                        'tier': 'db-custom-2-8192 (2 vCPU, 8 GB RAM)',
                        'high_availability': 'Regional with automatic failover',
                        'read_replicas': '1-2 for read scaling',
                        'backup': 'Automated daily backups, 7-day retention',
                        'encryption': 'Customer-managed encryption key (CMEK)'
                    }
                },
                'cache': {
                    'service': 'Memorystore (Redis)',
                    'purpose': 'Session storage, application caching',
                    'configuration': {
                        'tier': 'Basic (1 GB) or Standard (HA)',
                        'version': 'Redis 7.0',
                        'eviction_policy': 'allkeys-lru'
                    }
                },
                'messaging': {
                    'service': 'Pub/Sub',
                    'purpose': 'Asynchronous messaging between services',
                    'configuration': {
                        'topics': 'Per-domain event topics',
                        'subscriptions': 'Pull or push delivery',
                        'dead_letter': 'Dead letter topic after 5 retries',
                        'ordering': 'Ordering keys for ordered delivery'
                    }
                },
                'storage': {
                    'service': 'Cloud Storage',
                    'purpose': 'User uploads, backups, logs',
                    'configuration': {
                        'storage_class': 'Standard with lifecycle policies',
                        'versioning': 'Enabled for important buckets',
                        'lifecycle': 'Transition to Nearline after 30 days'
                    }
                }
            },
            'estimated_cost': {
                'monthly_usd': self._calculate_gke_cost(),
                'breakdown': {
                    'Cloud Load Balancing': '20-40 USD',
                    'GKE Autopilot': '75-250 USD',
                    'Cloud SQL': '80-250 USD',
                    'Memorystore': '30-80 USD',
                    'Pub/Sub': '5-20 USD',
                    'Cloud Storage': '5-20 USD'
                }
            },
            'pros': [
                'Kubernetes ecosystem compatibility',
                'Fine-grained scaling control',
                'Multi-cloud portability',
                'Rich service mesh (Anthos Service Mesh)',
                'Managed node provisioning with Autopilot'
            ],
            'cons': [
                'Higher baseline costs than serverless',
                'Kubernetes learning curve',
                'More operational complexity',
                'GKE management fee ($74.40/month per cluster)'
            ],
            'scaling_characteristics': {
                'users_supported': '10k - 500k',
                'requests_per_second': '1,000 - 50,000',
                'scaling_method': 'HPA + Cluster Autoscaler'
            }
        }
