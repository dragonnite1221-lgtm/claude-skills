# ruff: noqa: F403, F405, E501
"""
Azure cost optimization analyzer.
Analyzes Azure resource configurations and provides cost-saving recommendations.

Usage:
    python cost_optimizer.py --config resources.json
    python cost_optimizer.py --config resources.json --json
    python cost_optimizer.py --help

Expected JSON config format:
{
  "virtual_machines": [
    {"name": "vm-web-01", "size": "Standard_D4s_v5", "cpu_utilization": 12, "pricing": "on-demand", "monthly_cost": 140}
  ],
  "sql_databases": [
    {"name": "sqldb-main", "tier": "GeneralPurpose", "vcores": 8, "utilization": 25, "monthly_cost": 400}
  ],
  "storage_accounts": [
    {"name": "stmyapp", "size_gb": 500, "tier": "Hot", "has_lifecycle_policy": false}
  ],
  "aks_clusters": [
    {"name": "aks-prod", "node_count": 6, "node_size": "Standard_D4s_v5", "avg_cpu_utilization": 35, "monthly_cost": 800}
  ],
  "cosmos_db": [
    {"name": "cosmos-orders", "ru_provisioned": 10000, "ru_used_avg": 2000, "monthly_cost": 580}
  ],
  "public_ips": [
    {"name": "pip-unused", "attached": false}
  ],
  "app_services": [
    {"name": "app-web", "tier": "PremiumV3", "instance_count": 3, "cpu_utilization": 15, "monthly_cost": 300}
  ],
  "has_budget_alerts": false,
  "has_advisor_enabled": false
}
"""
import argparse
import json
import sys
from typing import Dict, List, Any


# fmt: off
__all__ = ['Any', 'Dict', 'List', 'argparse', 'json', 'sys']  # noqa: E501
# fmt: on
