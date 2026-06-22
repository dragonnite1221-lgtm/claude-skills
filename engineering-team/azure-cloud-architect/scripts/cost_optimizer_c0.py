# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from cost_optimizer_base import *  # noqa: F403,E402


class AzureCostOptimizerMixin0:
    """Analyze Azure resource configurations and recommend cost savings."""
    def __init__(self, resources: Dict[str, Any]):
        self.resources = resources
        self.recommendations: List[Dict[str, Any]] = []
    def analyze(self) -> Dict[str, Any]:
        """Run all analysis passes and return full report."""
        self.recommendations = []
        total_savings = 0.0

        total_savings += self._analyze_virtual_machines()
        total_savings += self._analyze_sql_databases()
        total_savings += self._analyze_storage()
        total_savings += self._analyze_aks()
        total_savings += self._analyze_cosmos_db()
        total_savings += self._analyze_app_services()
        total_savings += self._analyze_networking()
        total_savings += self._analyze_general()

        current_spend = self._estimate_current_spend()

        return {
            "current_monthly_usd": round(current_spend, 2),
            "potential_monthly_savings_usd": round(total_savings, 2),
            "optimized_monthly_usd": round(current_spend - total_savings, 2),
            "savings_percentage": round((total_savings / current_spend) * 100, 2) if current_spend > 0 else 0,
            "recommendations": self.recommendations,
            "priority_actions": self._top_priority(),
        }
    def _analyze_virtual_machines(self) -> float:
        savings = 0.0
        vms = self.resources.get("virtual_machines", [])

        for vm in vms:
            cost = vm.get("monthly_cost", 140)
            cpu = vm.get("cpu_utilization", 100)
            pricing = vm.get("pricing", "on-demand")

            # Idle VMs
            if cpu < 5:
                savings += cost * 0.9
                self.recommendations.append({
                    "service": "Virtual Machines",
                    "type": "Idle Resource",
                    "issue": f"VM {vm.get('name', '?')} has <5% CPU utilization",
                    "recommendation": "Deallocate or delete the VM. Use Azure Automation auto-shutdown for dev/test VMs.",
                    "potential_savings_usd": round(cost * 0.9, 2),
                    "priority": "high",
                })
            elif cpu < 20:
                savings += cost * 0.4
                self.recommendations.append({
                    "service": "Virtual Machines",
                    "type": "Right-sizing",
                    "issue": f"VM {vm.get('name', '?')} is under-utilized ({cpu}% CPU)",
                    "recommendation": "Downsize to a smaller SKU. Use Azure Advisor right-sizing recommendations.",
                    "potential_savings_usd": round(cost * 0.4, 2),
                    "priority": "high",
                })

            # Reserved Instances
            if pricing == "on-demand" and cpu >= 20:
                ri_savings = cost * 0.35
                savings += ri_savings
                self.recommendations.append({
                    "service": "Virtual Machines",
                    "type": "Reserved Instances",
                    "issue": f"VM {vm.get('name', '?')} runs on-demand with steady utilization",
                    "recommendation": "Purchase 1-year Reserved Instance (up to 35% savings) or 3-year (up to 55% savings).",
                    "potential_savings_usd": round(ri_savings, 2),
                    "priority": "medium",
                })

        # Spot VMs for batch/fault-tolerant workloads
        spot_candidates = [vm for vm in vms if vm.get("workload_type") in ("batch", "dev", "test")]
        if spot_candidates:
            spot_savings = sum(vm.get("monthly_cost", 100) * 0.6 for vm in spot_candidates)
            savings += spot_savings
            self.recommendations.append({
                "service": "Virtual Machines",
                "type": "Spot VMs",
                "issue": f"{len(spot_candidates)} VMs running batch/dev/test workloads on regular instances",
                "recommendation": "Switch to Azure Spot VMs for up to 90% savings on interruptible workloads.",
                "potential_savings_usd": round(spot_savings, 2),
                "priority": "medium",
            })

        return savings
