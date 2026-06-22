# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from architecture_designer_base import *  # noqa: F403,E402


ARCHITECTURE_PATTERNS = {
    "web_app": {
        "small": "app_service_web",
        "medium": "app_service_scaled",
        "large": "multi_region_web",
    },
    "saas_platform": {
        "small": "app_service_web",
        "medium": "aks_microservices",
        "large": "multi_region_web",
    },
    "mobile_backend": {
        "small": "serverless_functions",
        "medium": "app_service_web",
        "large": "aks_microservices",
    },
    "microservices": {
        "small": "container_apps",
        "medium": "aks_microservices",
        "large": "aks_microservices",
    },
    "data_pipeline": {
        "small": "serverless_data",
        "medium": "synapse_pipeline",
        "large": "synapse_pipeline",
    },
    "serverless": {
        "small": "serverless_functions",
        "medium": "serverless_functions",
        "large": "serverless_functions",
    },
}
def _size_bucket(users: int) -> str:
    if users < 10000:
        return "small"
    if users < 100000:
        return "medium"
    return "large"
def _app_service_web(users: int, reqs: Dict) -> Dict[str, Any]:
    budget = reqs.get("budget_monthly_usd", 500)
    return {
        "recommended_pattern": "app_service_web",
        "description": "Azure App Service with managed SQL and CDN",
        "use_case": "Web apps, SaaS platforms, startup MVPs",
        "service_stack": [
            "App Service (Linux P1v3)",
            "Azure SQL Database (Serverless GP_S_Gen5_2)",
            "Azure Front Door",
            "Azure Blob Storage",
            "Key Vault",
            "Entra ID + RBAC",
            "Application Insights",
        ],
        "estimated_monthly_cost_usd": min(280, budget),
        "cost_breakdown": {
            "App Service P1v3": "$70-95",
            "Azure SQL Serverless": "$40-120",
            "Front Door": "$35-55",
            "Blob Storage": "$5-15",
            "Key Vault": "$1-5",
            "Application Insights": "$5-20",
        },
        "pros": [
            "Managed platform — no OS patching",
            "Built-in autoscale and deployment slots",
            "Easy CI/CD with GitHub Actions or Azure DevOps",
            "Custom domains and TLS certificates included",
            "Integrated authentication (Easy Auth)",
        ],
        "cons": [
            "Less control than VMs or containers",
            "Platform constraints for exotic runtimes",
            "Cold start on lower-tier plans",
            "Outbound IP shared unless isolated tier",
        ],
        "scaling": {
            "users_supported": "1k - 100k",
            "requests_per_second": "100 - 10,000",
            "method": "App Service autoscale rules (CPU, memory, HTTP queue)",
        },
    }
def _aks_microservices(users: int, reqs: Dict) -> Dict[str, Any]:
    budget = reqs.get("budget_monthly_usd", 2000)
    return {
        "recommended_pattern": "aks_microservices",
        "description": "Microservices on AKS with API Management and Cosmos DB",
        "use_case": "Complex SaaS, multi-team microservices, high-scale platforms",
        "service_stack": [
            "AKS (3 node pools: system, app, jobs)",
            "API Management (Standard v2)",
            "Cosmos DB (multi-model)",
            "Service Bus (Standard)",
            "Azure Container Registry",
            "Azure Monitor + Application Insights",
            "Key Vault",
            "Entra ID workload identity",
        ],
        "estimated_monthly_cost_usd": min(1200, budget),
        "cost_breakdown": {
            "AKS node pools (D4s_v5 x3)": "$350-500",
            "API Management Standard v2": "$175",
            "Cosmos DB": "$100-400",
            "Service Bus Standard": "$10-50",
            "Container Registry Basic": "$5",
            "Azure Monitor": "$50-100",
            "Key Vault": "$1-5",
        },
        "pros": [
            "Full Kubernetes ecosystem",
            "Independent scaling per service",
            "Multi-language and multi-framework",
            "Mature ecosystem (Helm, Keda, Dapr)",
            "Workload identity — no credentials in pods",
        ],
        "cons": [
            "Kubernetes operational complexity",
            "Higher baseline cost",
            "Requires dedicated platform team",
            "Networking (CNI, ingress) configuration heavy",
        ],
        "scaling": {
            "users_supported": "10k - 10M",
            "requests_per_second": "1,000 - 1,000,000",
            "method": "Cluster autoscaler + KEDA event-driven autoscaling",
        },
    }
