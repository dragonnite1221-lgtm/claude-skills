# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from cost_optimizer_base import *  # noqa: F403,E402


class CostOptimizerMixin3:
    def _analyze_networking(self) -> float:
        """Analyze networking costs (egress, Cloud NAT, etc.)."""
        savings = 0.0

        cloud_nat_gateways = self.resources.get('cloud_nat_gateways', [])
        if len(cloud_nat_gateways) > 1:
            extra_nats = len(cloud_nat_gateways) - 1
            nat_savings = extra_nats * 45
            savings += nat_savings
            self.recommendations.append({
                'service': 'Cloud NAT',
                'type': 'Resource Consolidation',
                'issue': f'{len(cloud_nat_gateways)} Cloud NAT gateways deployed',
                'recommendation': 'Consolidate NAT gateways in dev/staging, or use Private Google Access for GCP services',
                'potential_savings': nat_savings,
                'priority': 'high'
            })

        egress_gb = self.resources.get('monthly_egress_gb', 0)
        if egress_gb > 1000:
            cdn_savings = egress_gb * 0.04  # CDN is cheaper than direct egress
            savings += cdn_savings
            self.recommendations.append({
                'service': 'Networking',
                'type': 'CDN Optimization',
                'issue': f'High egress volume ({egress_gb} GB/month)',
                'recommendation': 'Enable Cloud CDN to serve cached content at lower egress rates',
                'potential_savings': cdn_savings,
                'priority': 'medium'
            })

        return savings
    def _analyze_general_optimizations(self) -> float:
        """General GCP cost optimizations."""
        savings = 0.0

        # Log retention
        log_sinks = self.resources.get('log_sinks', [])
        if not log_sinks:
            log_volume_gb = self.resources.get('monthly_log_volume_gb', 0)
            if log_volume_gb > 50:
                log_savings = log_volume_gb * 0.50 * 0.6
                savings += log_savings
                self.recommendations.append({
                    'service': 'Cloud Logging',
                    'type': 'Log Exclusion',
                    'issue': f'{log_volume_gb} GB/month of logs without exclusion filters',
                    'recommendation': 'Create log exclusion filters for verbose/debug logs and route remaining to Cloud Storage via log sinks',
                    'potential_savings': log_savings,
                    'priority': 'medium'
                })

        # Unattached persistent disks
        persistent_disks = self.resources.get('persistent_disks', [])
        unattached = sum(1 for disk in persistent_disks if not disk.get('attached', True))
        if unattached > 0:
            disk_savings = unattached * 10  # ~$10/month per 100 GB disk
            savings += disk_savings
            self.recommendations.append({
                'service': 'Compute Engine',
                'type': 'Unused Resources',
                'issue': f'{unattached} unattached persistent disks',
                'recommendation': 'Snapshot and delete unused persistent disks',
                'potential_savings': disk_savings,
                'priority': 'high'
            })

        # Static external IPs
        static_ips = self.resources.get('static_ips', [])
        unused_ips = sum(1 for ip in static_ips if not ip.get('in_use', True))
        if unused_ips > 0:
            ip_savings = unused_ips * 7.30  # $0.01/hour = $7.30/month
            savings += ip_savings
            self.recommendations.append({
                'service': 'Networking',
                'type': 'Unused Resources',
                'issue': f'{unused_ips} unused static external IP addresses',
                'recommendation': 'Release unused static IPs to avoid hourly charges',
                'potential_savings': ip_savings,
                'priority': 'high'
            })

        # Budget alerts
        if not self.resources.get('has_budget_alerts', False):
            self.recommendations.append({
                'service': 'Cloud Billing',
                'type': 'Cost Monitoring',
                'issue': 'No budget alerts configured',
                'recommendation': 'Set up Cloud Billing budgets with alerts at 50%, 80%, 100% of monthly budget',
                'potential_savings': 0,
                'priority': 'high'
            })

        # Recommender API
        if not self.resources.get('uses_recommender', False):
            self.recommendations.append({
                'service': 'Active Assist',
                'type': 'Visibility',
                'issue': 'GCP Recommender not reviewed',
                'recommendation': 'Review Active Assist recommendations for right-sizing, idle resources, and committed use discounts',
                'potential_savings': 0,
                'priority': 'medium'
            })

        return savings
    def _prioritize_recommendations(self) -> List[Dict[str, Any]]:
        """Get top priority recommendations."""
        high_priority = [r for r in self.recommendations if r['priority'] == 'high']
        high_priority.sort(key=lambda x: x.get('potential_savings', 0), reverse=True)
        return high_priority[:5]
