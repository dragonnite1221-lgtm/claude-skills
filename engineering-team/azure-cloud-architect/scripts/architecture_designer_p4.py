# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from architecture_designer_base import *  # noqa: F403,E402


def generate_checklist(result: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Return an implementation checklist for the recommended architecture."""
    services = result.get("service_stack", [])
    return [
        {
            "phase": "Planning",
            "tasks": [
                "Review architecture pattern and Azure services",
                "Estimate costs with Azure Pricing Calculator",
                "Define environment strategy (dev, staging, production)",
                "Set up Azure subscription and resource groups",
                "Define tagging strategy (environment, owner, cost-center, app-name)",
            ],
        },
        {
            "phase": "Foundation",
            "tasks": [
                "Create VNet with subnets (app, data, management)",
                "Configure NSGs and Private Endpoints",
                "Set up Entra ID groups and RBAC assignments",
                "Create Key Vault and seed with initial secrets",
                "Enable Microsoft Defender for Cloud",
            ],
        },
        {
            "phase": "Core Services",
            "tasks": [f"Deploy {svc}" for svc in services],
        },
        {
            "phase": "Security",
            "tasks": [
                "Enable Managed Identity on all services",
                "Configure Private Endpoints for PaaS resources",
                "Set up Application Gateway or Front Door with WAF",
                "Assign Azure Policy initiatives (CIS, SOC 2, etc.)",
                "Enable diagnostic settings on all resources",
            ],
        },
        {
            "phase": "Monitoring",
            "tasks": [
                "Create Log Analytics workspace",
                "Enable Application Insights for all services",
                "Create Azure Monitor alert rules for critical metrics",
                "Set up Action Groups for notifications (email, Teams, PagerDuty)",
                "Create Azure Dashboard for operational visibility",
            ],
        },
        {
            "phase": "CI/CD",
            "tasks": [
                "Set up Azure DevOps or GitHub Actions pipeline",
                "Configure workload identity federation (no secrets in CI)",
                "Implement Bicep deployment pipeline with what-if preview",
                "Set up staging slots or blue-green deployment",
                "Document rollback procedures",
            ],
        },
    ]
def _format_text(result: Dict[str, Any]) -> str:
    lines = []
    lines.append(f"Pattern: {result['recommended_pattern']}")
    lines.append(f"Description: {result['description']}")
    lines.append(f"Use Case: {result['use_case']}")
    lines.append(f"Estimated Monthly Cost: ${result['estimated_monthly_cost_usd']}")
    lines.append("")
    lines.append("Service Stack:")
    for svc in result.get("service_stack", []):
        lines.append(f"  - {svc}")
    lines.append("")
    lines.append("Cost Breakdown:")
    for k, v in result.get("cost_breakdown", {}).items():
        lines.append(f"  {k}: {v}")
    lines.append("")
    lines.append("Pros:")
    for p in result.get("pros", []):
        lines.append(f"  + {p}")
    lines.append("")
    lines.append("Cons:")
    for c in result.get("cons", []):
        lines.append(f"  - {c}")
    if result.get("compliance_notes"):
        lines.append("")
        lines.append("Compliance Notes:")
        for note in result["compliance_notes"]:
            lines.append(f"  * {note}")
    lines.append("")
    lines.append("Scaling:")
    for k, v in result.get("scaling", {}).items():
        lines.append(f"  {k}: {v}")
    return "\n".join(lines)
