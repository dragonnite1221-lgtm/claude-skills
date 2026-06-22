# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from architecture_designer_base import *  # noqa: F403,E402
# fmt: off
from architecture_designer_p1 import ARCHITECTURE_PATTERNS, _aks_microservices, _app_service_web, _size_bucket  # noqa: E402,E501
from architecture_designer_p2 import _container_apps, _serverless_functions, _synapse_pipeline  # noqa: E402,E501
# fmt: on


def _serverless_data(users: int, reqs: Dict) -> Dict[str, Any]:
    budget = reqs.get("budget_monthly_usd", 300)
    return {
        "recommended_pattern": "serverless_data",
        "description": "Lightweight data pipeline with Functions and Data Lake",
        "use_case": "Small-scale ETL, event processing, log aggregation",
        "service_stack": [
            "Azure Functions",
            "Event Grid",
            "Data Lake Storage Gen2",
            "Azure SQL Serverless",
            "Application Insights",
        ],
        "estimated_monthly_cost_usd": min(120, budget),
        "cost_breakdown": {
            "Azure Functions": "$0-20",
            "Event Grid": "$0-5",
            "Data Lake Storage Gen2": "$5-20",
            "Azure SQL Serverless": "$20-60",
            "Application Insights": "$5-15",
        },
        "pros": [
            "Very low cost for small volumes",
            "Serverless end-to-end",
            "Simple to operate",
            "Scales automatically",
        ],
        "cons": [
            "Not suitable for high-volume analytics",
            "Limited transformation capabilities",
            "No built-in orchestration (use Durable Functions)",
        ],
        "scaling": {
            "events_per_second": "10 - 10,000",
            "data_volume": "1 MB - 100 GB per day",
            "method": "Azure Functions auto-scale",
        },
    }
def _multi_region_web(users: int, reqs: Dict) -> Dict[str, Any]:
    budget = reqs.get("budget_monthly_usd", 5000)
    return {
        "recommended_pattern": "multi_region_web",
        "description": "Multi-region active-active deployment with Front Door",
        "use_case": "Global applications, 99.99% uptime, data residency compliance",
        "service_stack": [
            "Azure Front Door (Premium)",
            "App Service (2+ regions) or AKS (2+ regions)",
            "Cosmos DB (multi-region writes)",
            "Azure SQL (geo-replication or failover groups)",
            "Traffic Manager (DNS failover)",
            "Azure Monitor + Log Analytics (centralized)",
            "Key Vault (per region)",
        ],
        "estimated_monthly_cost_usd": min(3000, budget),
        "cost_breakdown": {
            "Front Door Premium": "$100-200",
            "Compute (2 regions)": "$300-1000",
            "Cosmos DB (multi-region)": "$400-1500",
            "Azure SQL geo-replication": "$200-600",
            "Monitoring": "$50-150",
            "Data transfer (cross-region)": "$50-200",
        },
        "pros": [
            "Global low latency",
            "99.99% availability",
            "Automatic failover",
            "Data residency compliance",
            "Front Door WAF at the edge",
        ],
        "cons": [
            "1.5-2x cost vs single region",
            "Data consistency challenges (Cosmos DB conflict resolution)",
            "Complex deployment pipeline",
            "Cross-region data transfer costs",
        ],
        "scaling": {
            "users_supported": "100k - 100M",
            "requests_per_second": "10,000 - 10,000,000",
            "method": "Per-region autoscale + Front Door global routing",
        },
    }
PATTERN_DISPATCH = {
    "app_service_web": _app_service_web,
    "app_service_scaled": _app_service_web,  # same builder, cost adjusts
    "aks_microservices": _aks_microservices,
    "container_apps": _container_apps,
    "serverless_functions": _serverless_functions,
    "synapse_pipeline": _synapse_pipeline,
    "serverless_data": _serverless_data,
    "multi_region_web": _multi_region_web,
}
def recommend(app_type: str, users: int, requirements: Dict) -> Dict[str, Any]:
    """Return architecture recommendation for the given inputs."""
    bucket = _size_bucket(users)
    patterns = ARCHITECTURE_PATTERNS.get(app_type, ARCHITECTURE_PATTERNS["web_app"])
    pattern_key = patterns.get(bucket, "app_service_web")
    builder = PATTERN_DISPATCH.get(pattern_key, _app_service_web)
    result = builder(users, requirements)

    # Add compliance notes if relevant
    compliance = requirements.get("compliance", [])
    if compliance:
        result["compliance_notes"] = []
        if "HIPAA" in compliance:
            result["compliance_notes"].append(
                "Enable Microsoft Defender for Cloud, BAA agreement, audit logging, encryption at rest with CMK"
            )
        if "SOC2" in compliance:
            result["compliance_notes"].append(
                "Azure Policy SOC 2 initiative, Defender for Cloud regulatory compliance dashboard"
            )
        if "GDPR" in compliance:
            result["compliance_notes"].append(
                "Data residency in EU region, Purview for data classification, consent management"
            )
        if "ISO27001" in compliance or "ISO 27001" in compliance:
            result["compliance_notes"].append(
                "Azure Policy ISO 27001 initiative, audit logs to Log Analytics, access reviews in Entra ID"
            )

    return result
