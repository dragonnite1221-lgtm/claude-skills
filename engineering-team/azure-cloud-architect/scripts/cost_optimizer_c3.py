# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from cost_optimizer_base import *  # noqa: F403,E402


class AzureCostOptimizerMixin3:
    def _analyze_networking(self) -> float:
        savings = 0.0

        # Unattached public IPs
        pips = self.resources.get("public_ips", [])
        unattached = [p for p in pips if not p.get("attached", True)]
        if unattached:
            pip_savings = len(unattached) * 3.65  # ~$0.005/hr = $3.65/month
            savings += pip_savings
            self.recommendations.append({
                "service": "Public IP",
                "type": "Unused Resource",
                "issue": f"{len(unattached)} unattached public IPs incurring hourly charges",
                "recommendation": "Delete unused public IPs. Unattached Standard SKU IPs cost ~$3.65/month each.",
                "potential_savings_usd": round(pip_savings, 2),
                "priority": "high",
            })

        # NAT Gateway in dev environments
        nat_gateways = self.resources.get("nat_gateways", [])
        dev_nats = [n for n in nat_gateways if n.get("environment") in ("dev", "test")]
        if dev_nats:
            nat_savings = len(dev_nats) * 32  # ~$32/month per NAT Gateway
            savings += nat_savings
            self.recommendations.append({
                "service": "NAT Gateway",
                "type": "Environment Optimization",
                "issue": f"{len(dev_nats)} NAT Gateways in dev/test environments",
                "recommendation": "Remove NAT Gateways in dev/test. Use Azure Firewall or service tags for outbound instead.",
                "potential_savings_usd": round(nat_savings, 2),
                "priority": "medium",
            })

        return savings
    def _analyze_general(self) -> float:
        savings = 0.0

        if not self.resources.get("has_budget_alerts", False):
            self.recommendations.append({
                "service": "Cost Management",
                "type": "Budget Alerts",
                "issue": "No budget alerts configured",
                "recommendation": "Create Azure Budget with alerts at 50%, 80%, and 100% of monthly target.",
                "potential_savings_usd": 0,
                "priority": "high",
            })

        if not self.resources.get("has_advisor_enabled", True):
            self.recommendations.append({
                "service": "Azure Advisor",
                "type": "Visibility",
                "issue": "Azure Advisor cost recommendations not reviewed",
                "recommendation": "Review Azure Advisor cost recommendations weekly. Enable Advisor alerts for new findings.",
                "potential_savings_usd": 0,
                "priority": "medium",
            })

        return savings
    def _estimate_current_spend(self) -> float:
        total = 0.0
        for key in ("virtual_machines", "sql_databases", "aks_clusters", "cosmos_db", "app_services"):
            for item in self.resources.get(key, []):
                total += item.get("monthly_cost", 0)
        # Storage estimate
        for acct in self.resources.get("storage_accounts", []):
            total += acct.get("size_gb", 0) * 0.018  # Hot tier default
        # Public IPs
        for pip in self.resources.get("public_ips", []):
            total += 3.65
        return total if total > 0 else 1000  # Default if no cost data
    def _top_priority(self) -> List[Dict[str, Any]]:
        high = [r for r in self.recommendations if r["priority"] == "high"]
        high.sort(key=lambda x: x.get("potential_savings_usd", 0), reverse=True)
        return high[:5]
