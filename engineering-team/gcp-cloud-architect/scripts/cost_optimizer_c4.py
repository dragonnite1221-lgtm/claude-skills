# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from cost_optimizer_base import *  # noqa: F403,E402


class CostOptimizerMixin4:
    def generate_optimization_checklist(self) -> List[Dict[str, Any]]:
        """Generate actionable checklist for cost optimization."""
        return [
            {
                'category': 'Immediate Actions (Today)',
                'items': [
                    'Release unused static IPs',
                    'Delete unattached persistent disks',
                    'Stop idle Compute Engine instances',
                    'Set up billing budget alerts'
                ]
            },
            {
                'category': 'This Week',
                'items': [
                    'Add Cloud Storage lifecycle policies',
                    'Create log exclusion filters for verbose logs',
                    'Right-size Cloud SQL instances',
                    'Review Active Assist recommendations'
                ]
            },
            {
                'category': 'This Month',
                'items': [
                    'Evaluate committed use discounts',
                    'Migrate GKE Standard to Autopilot where applicable',
                    'Partition and cluster BigQuery tables',
                    'Enable Cloud CDN for high-egress services'
                ]
            },
            {
                'category': 'Ongoing',
                'items': [
                    'Review billing reports weekly',
                    'Label all resources for cost allocation',
                    'Monitor Active Assist recommendations monthly',
                    'Conduct quarterly cost optimization reviews'
                ]
            }
        ]
