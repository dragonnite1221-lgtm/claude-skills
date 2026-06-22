# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from architecture_designer_base import *  # noqa: F403,E402


class ArchitectureDesignerMixin7:
    def _calculate_data_pipeline_cost(self) -> float:
        """Estimate data pipeline cost."""
        pubsub_cost = max(5, self.data_size_gb * 0.5)
        dataflow_cost = max(20, self.data_size_gb * 1.5)
        bigquery_cost = max(10, self.data_size_gb * 0.02 * 6.25)
        storage_cost = self.data_size_gb * 0.02

        total = pubsub_cost + dataflow_cost + bigquery_cost + storage_cost
        return min(total, self.budget_monthly)
    def generate_service_checklist(self) -> list:
        """Generate implementation checklist for recommended architecture."""
        architecture = self.recommend_architecture_pattern()

        checklist = [
            {
                'phase': 'Planning',
                'tasks': [
                    'Review architecture pattern and services',
                    'Estimate costs using GCP Pricing Calculator',
                    'Define environment strategy (dev, staging, prod)',
                    'Set up GCP Organization and projects',
                    'Define labeling strategy for resources'
                ]
            },
            {
                'phase': 'Foundation',
                'tasks': [
                    'Create VPC with subnets (if using GKE/Compute)',
                    'Configure Cloud NAT for private resources',
                    'Set up IAM roles and service accounts',
                    'Enable Cloud Audit Logs',
                    'Configure Organization policies'
                ]
            },
            {
                'phase': 'Core Services',
                'tasks': [
                    f"Deploy {service['service']}"
                    for service in architecture['services'].values()
                ]
            },
            {
                'phase': 'Security',
                'tasks': [
                    'Configure firewall rules and VPC Service Controls',
                    'Enable encryption (Cloud KMS) for all services',
                    'Set up Cloud Armor WAF rules',
                    'Configure Secret Manager for credentials',
                    'Enable Security Command Center'
                ]
            },
            {
                'phase': 'Monitoring',
                'tasks': [
                    'Create Cloud Monitoring dashboards',
                    'Set up alerting policies for critical metrics',
                    'Configure notification channels (email, Slack, PagerDuty)',
                    'Enable Cloud Trace for distributed tracing',
                    'Set up log-based metrics and log sinks'
                ]
            },
            {
                'phase': 'CI/CD',
                'tasks': [
                    'Set up Cloud Build triggers',
                    'Configure automated testing',
                    'Implement canary or rolling deployments',
                    'Set up rollback procedures',
                    'Document deployment process'
                ]
            }
        ]

        return checklist
