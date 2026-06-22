# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from architecture_designer_base import *  # noqa: F403,E402


def _container_apps(users: int, reqs: Dict) -> Dict[str, Any]:
    budget = reqs.get("budget_monthly_usd", 500)
    return {
        "recommended_pattern": "container_apps",
        "description": "Serverless containers on Azure Container Apps",
        "use_case": "Microservices without Kubernetes management overhead",
        "service_stack": [
            "Azure Container Apps",
            "Azure Container Registry",
            "Cosmos DB",
            "Service Bus",
            "Key Vault",
            "Application Insights",
            "Entra ID managed identity",
        ],
        "estimated_monthly_cost_usd": min(350, budget),
        "cost_breakdown": {
            "Container Apps (consumption)": "$50-150",
            "Container Registry Basic": "$5",
            "Cosmos DB": "$50-150",
            "Service Bus Standard": "$10-30",
            "Key Vault": "$1-5",
            "Application Insights": "$5-20",
        },
        "pros": [
            "Serverless containers — scale to zero",
            "Built-in Dapr integration",
            "KEDA autoscaling included",
            "No cluster management",
            "Simpler networking than AKS",
        ],
        "cons": [
            "Less control than full AKS",
            "Limited to HTTP and event-driven workloads",
            "Smaller ecosystem than Kubernetes",
            "Some advanced features still in preview",
        ],
        "scaling": {
            "users_supported": "1k - 500k",
            "requests_per_second": "100 - 50,000",
            "method": "KEDA scalers (HTTP, queue length, CPU, custom)",
        },
    }
def _serverless_functions(users: int, reqs: Dict) -> Dict[str, Any]:
    budget = reqs.get("budget_monthly_usd", 300)
    return {
        "recommended_pattern": "serverless_functions",
        "description": "Azure Functions with Event Grid and Cosmos DB",
        "use_case": "Event-driven backends, APIs, scheduled jobs, webhooks",
        "service_stack": [
            "Azure Functions (Consumption plan)",
            "Event Grid",
            "Service Bus",
            "Cosmos DB (Serverless)",
            "Azure Blob Storage",
            "Application Insights",
            "Key Vault",
        ],
        "estimated_monthly_cost_usd": min(80, budget),
        "cost_breakdown": {
            "Functions (Consumption)": "$0-20 (1M free executions/month)",
            "Event Grid": "$0-5",
            "Service Bus Basic": "$0-10",
            "Cosmos DB Serverless": "$5-40",
            "Blob Storage": "$2-10",
            "Application Insights": "$5-15",
        },
        "pros": [
            "Pay-per-execution — true serverless",
            "Scale to zero, scale to millions",
            "Multiple trigger types (HTTP, queue, timer, blob, event)",
            "Durable Functions for orchestration",
            "Fast development cycle",
        ],
        "cons": [
            "Cold start latency (1-5s on consumption plan)",
            "10-minute execution timeout on consumption plan",
            "Limited local development experience",
            "Debugging distributed functions is complex",
        ],
        "scaling": {
            "users_supported": "1k - 1M",
            "requests_per_second": "100 - 100,000",
            "method": "Automatic (Azure Functions runtime scales instances)",
        },
    }
def _synapse_pipeline(users: int, reqs: Dict) -> Dict[str, Any]:
    budget = reqs.get("budget_monthly_usd", 1500)
    return {
        "recommended_pattern": "synapse_pipeline",
        "description": "Data pipeline with Event Hubs, Synapse, and Data Lake",
        "use_case": "Data warehousing, ETL, analytics, ML pipelines",
        "service_stack": [
            "Event Hubs (Standard)",
            "Data Factory / Synapse Pipelines",
            "Data Lake Storage Gen2",
            "Synapse Analytics (Serverless SQL pool)",
            "Azure Functions (processing)",
            "Power BI",
            "Azure Monitor",
        ],
        "estimated_monthly_cost_usd": min(800, budget),
        "cost_breakdown": {
            "Event Hubs Standard": "$20-80",
            "Data Factory": "$50-200",
            "Data Lake Storage Gen2": "$20-80",
            "Synapse Serverless SQL": "$50-300 (per TB scanned)",
            "Azure Functions": "$10-40",
            "Power BI Pro": "$10/user/month",
        },
        "pros": [
            "Unified analytics platform (Synapse)",
            "Serverless SQL — pay per query",
            "Native Spark integration",
            "Data Lake Gen2 — hierarchical namespace, cheap storage",
            "Built-in data integration (90+ connectors)",
        ],
        "cons": [
            "Synapse learning curve",
            "Cost unpredictable with serverless SQL at scale",
            "Complex permissions model (Synapse RBAC + storage ACLs)",
            "Spark pool startup time",
        ],
        "scaling": {
            "events_per_second": "1,000 - 10,000,000",
            "data_volume": "1 GB - 1 PB per day",
            "method": "Event Hubs throughput units + Synapse auto-scale",
        },
    }
