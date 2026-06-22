# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from cost_optimizer_base import *  # noqa: F403,E402


class CostOptimizerMixin1:
    def _analyze_compute(self) -> float:
        """Analyze compute resources (GCE, GKE, Cloud Run)."""
        savings = 0.0

        gce_instances = self.resources.get('gce_instances', [])
        if gce_instances:
            idle_count = sum(1 for inst in gce_instances if inst.get('cpu_utilization', 100) < 10)
            if idle_count > 0:
                idle_cost = idle_count * 50
                savings += idle_cost
                self.recommendations.append({
                    'service': 'Compute Engine',
                    'type': 'Idle Resources',
                    'issue': f'{idle_count} GCE instances with <10% CPU utilization',
                    'recommendation': 'Stop or delete idle instances, or downsize to smaller machine types',
                    'potential_savings': idle_cost,
                    'priority': 'high'
                })

            # Check for committed use discounts
            on_demand_count = sum(1 for inst in gce_instances if inst.get('pricing', 'on-demand') == 'on-demand')
            if on_demand_count >= 2:
                cud_savings = on_demand_count * 50 * 0.37  # 37% savings with 1-yr CUD
                savings += cud_savings
                self.recommendations.append({
                    'service': 'Compute Engine',
                    'type': 'Committed Use Discounts',
                    'issue': f'{on_demand_count} instances on on-demand pricing',
                    'recommendation': 'Purchase 1-year committed use discounts for predictable workloads (37% savings) or 3-year (55% savings)',
                    'potential_savings': cud_savings,
                    'priority': 'medium'
                })

            # Check for sustained use discounts awareness
            short_lived = sum(1 for inst in gce_instances if inst.get('uptime_hours_month', 730) < 200)
            if short_lived > 0:
                self.recommendations.append({
                    'service': 'Compute Engine',
                    'type': 'Scheduling',
                    'issue': f'{short_lived} instances running <200 hours/month',
                    'recommendation': 'Use Instance Scheduler to stop dev/test instances outside business hours',
                    'potential_savings': short_lived * 20,
                    'priority': 'medium'
                })
                savings += short_lived * 20

        # GKE optimization
        gke_clusters = self.resources.get('gke_clusters', [])
        for cluster in gke_clusters:
            if cluster.get('mode', 'standard') == 'standard':
                node_utilization = cluster.get('avg_node_utilization', 100)
                if node_utilization < 40:
                    autopilot_savings = cluster.get('monthly_cost', 500) * 0.30
                    savings += autopilot_savings
                    self.recommendations.append({
                        'service': 'GKE',
                        'type': 'Cluster Mode',
                        'issue': f'Standard GKE cluster with <40% node utilization',
                        'recommendation': 'Migrate to GKE Autopilot to pay only for pod resources, or enable cluster autoscaler',
                        'potential_savings': autopilot_savings,
                        'priority': 'high'
                    })

        # Cloud Run optimization
        cloud_run_services = self.resources.get('cloud_run_services', [])
        for svc in cloud_run_services:
            if svc.get('min_instances', 0) > 0 and svc.get('avg_rps', 100) < 1:
                min_inst_savings = svc.get('min_instances', 1) * 15
                savings += min_inst_savings
                self.recommendations.append({
                    'service': 'Cloud Run',
                    'type': 'Min Instances',
                    'issue': f'Service {svc.get("name", "unknown")} has min instances but very low traffic',
                    'recommendation': 'Set min-instances to 0 for low-traffic services to enable scale-to-zero',
                    'potential_savings': min_inst_savings,
                    'priority': 'medium'
                })

        return savings
