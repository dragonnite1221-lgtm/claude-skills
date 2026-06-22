# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from cost_optimizer_base import *  # noqa: F403,E402


class AzureCostOptimizerMixin2:
    def _analyze_aks(self) -> float:
        savings = 0.0
        clusters = self.resources.get("aks_clusters", [])

        for cluster in clusters:
            cost = cluster.get("monthly_cost", 500)
            cpu = cluster.get("avg_cpu_utilization", 100)
            node_count = cluster.get("node_count", 3)

            # Over-provisioned cluster
            if cpu < 30 and node_count > 3:
                aks_savings = cost * 0.3
                savings += aks_savings
                self.recommendations.append({
                    "service": "AKS",
                    "type": "Right-sizing",
                    "issue": f"Cluster {cluster.get('name', '?')} has {node_count} nodes at {cpu}% CPU",
                    "recommendation": "Enable cluster autoscaler. Set min nodes to 2 (or 1 for dev). Use node auto-provisioning.",
                    "potential_savings_usd": round(aks_savings, 2),
                    "priority": "high",
                })

            # Spot node pools for non-critical workloads
            if not cluster.get("has_spot_pool", False):
                spot_savings = cost * 0.15
                savings += spot_savings
                self.recommendations.append({
                    "service": "AKS",
                    "type": "Spot Node Pools",
                    "issue": f"Cluster {cluster.get('name', '?')} has no spot node pools",
                    "recommendation": "Add a spot node pool for batch jobs, CI runners, and dev workloads (up to 90% savings).",
                    "potential_savings_usd": round(spot_savings, 2),
                    "priority": "medium",
                })

        return savings
    def _analyze_cosmos_db(self) -> float:
        savings = 0.0
        dbs = self.resources.get("cosmos_db", [])

        for db in dbs:
            cost = db.get("monthly_cost", 200)
            ru_provisioned = db.get("ru_provisioned", 400)
            ru_used = db.get("ru_used_avg", 400)

            # Massive over-provisioning
            if ru_provisioned > 0 and ru_used / ru_provisioned < 0.2:
                cosmos_savings = cost * 0.5
                savings += cosmos_savings
                self.recommendations.append({
                    "service": "Cosmos DB",
                    "type": "Right-sizing",
                    "issue": f"Container {db.get('name', '?')} uses {ru_used}/{ru_provisioned} RU/s ({int(ru_used/ru_provisioned*100)}% utilization)",
                    "recommendation": "Switch to autoscale throughput or serverless mode. Autoscale adjusts RU/s between 10%-100% of max.",
                    "potential_savings_usd": round(cosmos_savings, 2),
                    "priority": "high",
                })
            elif ru_provisioned > 0 and ru_used / ru_provisioned < 0.5:
                cosmos_savings = cost * 0.25
                savings += cosmos_savings
                self.recommendations.append({
                    "service": "Cosmos DB",
                    "type": "Autoscale",
                    "issue": f"Container {db.get('name', '?')} uses {ru_used}/{ru_provisioned} RU/s — variable workload",
                    "recommendation": "Enable autoscale throughput. Set max RU/s to current provisioned value.",
                    "potential_savings_usd": round(cosmos_savings, 2),
                    "priority": "medium",
                })

        return savings
    def _analyze_app_services(self) -> float:
        savings = 0.0
        apps = self.resources.get("app_services", [])

        for app in apps:
            cost = app.get("monthly_cost", 100)
            cpu = app.get("cpu_utilization", 100)
            instances = app.get("instance_count", 1)
            tier = app.get("tier", "Basic")

            # Over-provisioned instances
            if cpu < 20 and instances > 1:
                app_savings = cost * 0.4
                savings += app_savings
                self.recommendations.append({
                    "service": "App Service",
                    "type": "Right-sizing",
                    "issue": f"App {app.get('name', '?')} runs {instances} instances at {cpu}% CPU",
                    "recommendation": "Reduce instance count or enable autoscale with min=1. Consider downgrading plan tier.",
                    "potential_savings_usd": round(app_savings, 2),
                    "priority": "high",
                })

            # Premium tier for dev/test
            if tier in ("PremiumV3", "PremiumV2") and app.get("environment") in ("dev", "test"):
                tier_savings = cost * 0.5
                savings += tier_savings
                self.recommendations.append({
                    "service": "App Service",
                    "type": "Plan Tier",
                    "issue": f"App {app.get('name', '?')} uses {tier} in {app.get('environment', 'unknown')} environment",
                    "recommendation": "Use Basic (B1) or Free tier for dev/test environments.",
                    "potential_savings_usd": round(tier_savings, 2),
                    "priority": "high",
                })

        return savings
