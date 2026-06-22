# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from risk_assessment_base import *  # noqa: F403,E402
# fmt: off
from risk_assessment_p1 import TREATMENT_OPTIONS  # noqa: E402,E501
from risk_assessment_p2 import calculate_residual_risk  # noqa: E402,E501
# fmt: on


def generate_report(
    scope: str,
    template: str,
    assets: List[Dict[str, Any]],
    risks: List[Dict[str, Any]],
    output_format: str
) -> str:
    """Generate risk assessment report."""
    timestamp = datetime.now().isoformat()

    # Calculate summary statistics
    risk_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "minimal": 0}
    for risk in risks:
        risk_counts[risk["level"]] += 1

    report_data = {
        "metadata": {
            "scope": scope,
            "template": template,
            "timestamp": timestamp,
            "methodology": "ISO 27001 Clause 6.1.2",
        },
        "summary": {
            "total_assets": len(assets),
            "total_risks": len(risks),
            "risk_distribution": risk_counts,
            "critical_risks": risk_counts["critical"],
            "high_risks": risk_counts["high"],
        },
        "assets": assets,
        "risks": risks,
        "residual_risks": [calculate_residual_risk(r) for r in risks[:10]],  # Top 10
    }

    if output_format == "json":
        return json.dumps(report_data, indent=2)
    elif output_format == "csv":
        lines = ["risk_id,asset,threat,likelihood,impact,score,level,treatment"]
        for risk in risks:
            lines.append(
                f"{risk['id']},{risk['asset_name']},{risk['threat_name']},"
                f"{risk['likelihood']},{risk['impact']},{risk['score']},"
                f"{risk['level']},{risk['treatment']}"
            )
        return "\n".join(lines)
    else:  # markdown
        lines = [
            f"# Security Risk Assessment Report",
            f"",
            f"**Scope:** {scope}",
            f"**Template:** {template}",
            f"**Date:** {timestamp}",
            f"**Methodology:** ISO 27001 Clause 6.1.2",
            f"",
            f"## Summary",
            f"",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| Total Assets | {len(assets)} |",
            f"| Total Risks | {len(risks)} |",
            f"| Critical Risks | {risk_counts['critical']} |",
            f"| High Risks | {risk_counts['high']} |",
            f"| Medium Risks | {risk_counts['medium']} |",
            f"",
            f"## Asset Inventory",
            f"",
            f"| ID | Asset | Type | Owner | Classification |",
            f"|----|-------|------|-------|----------------|",
        ]
        for asset in assets:
            lines.append(
                f"| {asset['id']} | {asset['name']} | {asset['type']} | "
                f"{asset['owner']} | {asset['classification'].capitalize()} |"
            )

        lines.extend([
            f"",
            f"## Risk Register",
            f"",
            f"| Risk ID | Asset | Threat | L | I | Score | Level |",
            f"|---------|-------|--------|---|---|-------|-------|",
        ])
        for risk in risks[:20]:  # Top 20 risks
            lines.append(
                f"| {risk['id']} | {risk['asset_name']} | {risk['threat_name']} | "
                f"{risk['likelihood']} | {risk['impact']} | {risk['score']} | "
                f"{risk['level'].capitalize()} |"
            )

        lines.extend([
            f"",
            f"## Treatment Recommendations",
            f"",
        ])
        for level, treatment in TREATMENT_OPTIONS.items():
            count = risk_counts[level]
            if count > 0:
                lines.append(f"**{level.capitalize()} ({count} risks):** {treatment}")

        return "\n".join(lines)
