# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from cost_optimizer_base import *  # noqa: F403,E402


class AzureCostOptimizerMixin1:
    def _analyze_sql_databases(self) -> float:
        savings = 0.0
        dbs = self.resources.get("sql_databases", [])

        for db in dbs:
            cost = db.get("monthly_cost", 200)
            utilization = db.get("utilization", 100)
            vcores = db.get("vcores", 2)
            tier = db.get("tier", "GeneralPurpose")

            # Idle databases
            if db.get("connections_per_day", 1000) < 10:
                savings += cost * 0.8
                self.recommendations.append({
                    "service": "Azure SQL",
                    "type": "Idle Resource",
                    "issue": f"Database {db.get('name', '?')} has <10 connections/day",
                    "recommendation": "Delete unused database or switch to serverless tier with auto-pause.",
                    "potential_savings_usd": round(cost * 0.8, 2),
                    "priority": "high",
                })

            # Serverless opportunity
            elif utilization < 30 and tier == "GeneralPurpose":
                serverless_savings = cost * 0.45
                savings += serverless_savings
                self.recommendations.append({
                    "service": "Azure SQL",
                    "type": "Serverless Migration",
                    "issue": f"Database {db.get('name', '?')} has low utilization ({utilization}%) on provisioned tier",
                    "recommendation": "Switch to Azure SQL Serverless tier with auto-pause (60-min delay). Pay only for active compute.",
                    "potential_savings_usd": round(serverless_savings, 2),
                    "priority": "high",
                })

            # Right-sizing
            elif utilization < 50 and vcores > 2:
                right_size_savings = cost * 0.3
                savings += right_size_savings
                self.recommendations.append({
                    "service": "Azure SQL",
                    "type": "Right-sizing",
                    "issue": f"Database {db.get('name', '?')} uses {vcores} vCores at {utilization}% utilization",
                    "recommendation": f"Reduce to {max(2, vcores // 2)} vCores. Monitor DTU/vCore usage after change.",
                    "potential_savings_usd": round(right_size_savings, 2),
                    "priority": "medium",
                })

        return savings
    def _analyze_storage(self) -> float:
        savings = 0.0
        accounts = self.resources.get("storage_accounts", [])

        for acct in accounts:
            size_gb = acct.get("size_gb", 0)
            tier = acct.get("tier", "Hot")

            # Lifecycle policy missing
            if not acct.get("has_lifecycle_policy", False) and size_gb > 50:
                lifecycle_savings = size_gb * 0.01  # ~$0.01/GB moving hot to cool
                savings += lifecycle_savings
                self.recommendations.append({
                    "service": "Blob Storage",
                    "type": "Lifecycle Policy",
                    "issue": f"Account {acct.get('name', '?')} ({size_gb} GB) has no lifecycle policy",
                    "recommendation": "Add lifecycle management: move to Cool after 30 days, Archive after 90 days.",
                    "potential_savings_usd": round(lifecycle_savings, 2),
                    "priority": "medium",
                })

            # Hot tier for large, infrequently accessed data
            if tier == "Hot" and size_gb > 500:
                tier_savings = size_gb * 0.008
                savings += tier_savings
                self.recommendations.append({
                    "service": "Blob Storage",
                    "type": "Storage Tier",
                    "issue": f"Account {acct.get('name', '?')} ({size_gb} GB) on Hot tier",
                    "recommendation": "Evaluate Cool or Cold tier for infrequently accessed data. Hot=$0.018/GB, Cool=$0.01/GB, Cold=$0.0036/GB.",
                    "potential_savings_usd": round(tier_savings, 2),
                    "priority": "high",
                })

        return savings
