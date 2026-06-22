# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from risk_assessment_base import *  # noqa: F403,E402
# fmt: off
from risk_assessment_p1 import CLASSIFICATION_CRITERIA, THREAT_CATALOGS, TREATMENT_OPTIONS, VULNERABILITY_PATTERNS, calculate_risk_score, get_risk_level  # noqa: E402,E501
# fmt: on


def generate_sample_assets(scope: str, template: str) -> List[Dict[str, Any]]:
    """Generate sample asset inventory based on scope and template."""
    base_assets = []

    if template == "healthcare":
        base_assets = [
            {"id": "A001", "name": "Patient Database", "type": "Information", "owner": "DBA Team", "classification": "critical"},
            {"id": "A002", "name": "EHR Application", "type": "Software", "owner": "App Team", "classification": "critical"},
            {"id": "A003", "name": "Medical Imaging System", "type": "Software", "owner": "Radiology", "classification": "high"},
            {"id": "A004", "name": "Database Servers", "type": "Hardware", "owner": "Infrastructure", "classification": "high"},
            {"id": "A005", "name": "Admin Credentials", "type": "Access", "owner": "Security", "classification": "critical"},
            {"id": "A006", "name": "Backup Systems", "type": "Service", "owner": "IT Ops", "classification": "high"},
            {"id": "A007", "name": "Network Infrastructure", "type": "Hardware", "owner": "Network Team", "classification": "high"},
            {"id": "A008", "name": "API Gateway", "type": "Software", "owner": "Platform Team", "classification": "high"},
        ]
    elif template == "cloud":
        base_assets = [
            {"id": "A001", "name": "Cloud Storage Buckets", "type": "Service", "owner": "Platform", "classification": "high"},
            {"id": "A002", "name": "Container Registry", "type": "Service", "owner": "DevOps", "classification": "high"},
            {"id": "A003", "name": "API Services", "type": "Software", "owner": "Engineering", "classification": "critical"},
            {"id": "A004", "name": "Database Instances", "type": "Service", "owner": "DBA Team", "classification": "critical"},
            {"id": "A005", "name": "IAM Configuration", "type": "Access", "owner": "Security", "classification": "critical"},
            {"id": "A006", "name": "Secrets Manager", "type": "Service", "owner": "Security", "classification": "critical"},
            {"id": "A007", "name": "Load Balancers", "type": "Infrastructure", "owner": "Platform", "classification": "high"},
            {"id": "A008", "name": "Monitoring Systems", "type": "Service", "owner": "SRE", "classification": "medium"},
        ]
    else:  # general
        base_assets = [
            {"id": "A001", "name": "Corporate Data", "type": "Information", "owner": "Data Team", "classification": "high"},
            {"id": "A002", "name": "Business Applications", "type": "Software", "owner": "IT", "classification": "high"},
            {"id": "A003", "name": "Server Infrastructure", "type": "Hardware", "owner": "Infrastructure", "classification": "high"},
            {"id": "A004", "name": "User Credentials", "type": "Access", "owner": "Security", "classification": "critical"},
            {"id": "A005", "name": "Email System", "type": "Service", "owner": "IT", "classification": "medium"},
            {"id": "A006", "name": "File Servers", "type": "Hardware", "owner": "Infrastructure", "classification": "medium"},
            {"id": "A007", "name": "Network Equipment", "type": "Hardware", "owner": "Network", "classification": "high"},
            {"id": "A008", "name": "Backup Infrastructure", "type": "Service", "owner": "IT Ops", "classification": "high"},
        ]

    # Tag assets with scope
    for asset in base_assets:
        asset["scope"] = scope

    return base_assets
def assess_risks(
    assets: List[Dict[str, Any]],
    template: str
) -> List[Dict[str, Any]]:
    """Perform risk assessment on assets."""
    threats = THREAT_CATALOGS.get(template, THREAT_CATALOGS["general"])
    risks = []
    risk_id = 1

    for asset in assets:
        classification = asset.get("classification", "medium")
        impact = CLASSIFICATION_CRITERIA.get(classification, {}).get("impact", 3)

        # Map relevant threats to asset
        relevant_threats = threats[:5]  # Top 5 threats for each asset

        for threat in relevant_threats:
            likelihood = threat["likelihood"]
            score = calculate_risk_score(likelihood, impact)
            level = get_risk_level(score)

            # Identify potential vulnerabilities
            vuln_category = threat["category"].lower()
            vulns = VULNERABILITY_PATTERNS.get("technical", ["Unknown vulnerability"])
            if "access" in vuln_category:
                vulns = VULNERABILITY_PATTERNS["access"]
            elif "personnel" in vuln_category or "social" in vuln_category:
                vulns = VULNERABILITY_PATTERNS["people"]

            risk = {
                "id": f"R{risk_id:03d}",
                "asset_id": asset["id"],
                "asset_name": asset["name"],
                "threat_id": threat["id"],
                "threat_name": threat["name"],
                "threat_category": threat["category"],
                "vulnerability": vulns[0] if vulns else "Unidentified",
                "likelihood": likelihood,
                "impact": impact,
                "score": score,
                "level": level,
                "treatment": TREATMENT_OPTIONS.get(level, "Review required"),
            }
            risks.append(risk)
            risk_id += 1

    # Sort by risk score descending
    risks.sort(key=lambda x: x["score"], reverse=True)
    return risks
def calculate_residual_risk(risk: Dict[str, Any], control_effectiveness: float = 0.7) -> Dict[str, Any]:
    """Calculate residual risk after applying controls."""
    residual_likelihood = max(1, int(risk["likelihood"] * (1 - control_effectiveness)))
    residual_score = calculate_risk_score(residual_likelihood, risk["impact"])

    return {
        "risk_id": risk["id"],
        "inherent_score": risk["score"],
        "control_effectiveness": control_effectiveness,
        "residual_likelihood": residual_likelihood,
        "residual_score": residual_score,
        "residual_level": get_risk_level(residual_score),
    }
