# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from isms_audit_scheduler_base import *  # noqa: F403,E402
# fmt: off
from isms_audit_scheduler_p1 import AUDIT_FREQUENCY, DEFAULT_RISK_RATINGS, calculate_audit_dates  # noqa: E402,E501
# fmt: on


def generate_audit_plan(
    year: int,
    controls: Optional[Dict[str, Dict]] = None
) -> Dict[str, Any]:
    """Generate risk-based annual audit plan."""
    if controls is None:
        controls = DEFAULT_RISK_RATINGS

    plan = {
        "metadata": {
            "year": year,
            "generated": datetime.now().isoformat(),
            "methodology": "ISO 27001 Risk-Based Internal Auditing",
            "total_controls": len(controls),
        },
        "schedule": {
            "Q1": {"month": "February-March", "audits": []},
            "Q2": {"month": "May-June", "audits": []},
            "Q3": {"month": "August-September", "audits": []},
            "Q4": {"month": "November", "audits": []},
        },
        "controls": {},
    }

    # Assign controls to quarters based on risk
    for control_id, control_data in controls.items():
        risk = control_data.get("risk", "medium")
        frequency = AUDIT_FREQUENCY.get(risk, 1)
        audit_dates = calculate_audit_dates(year, frequency)

        plan["controls"][control_id] = {
            "name": control_data.get("name", "Unknown"),
            "risk": risk,
            "frequency": frequency,
            "scheduled_audits": audit_dates,
        }

        # Add to quarterly schedule
        for i, date in enumerate(audit_dates):
            month = int(date.split("-")[1])
            if month <= 3:
                quarter = "Q1"
            elif month <= 6:
                quarter = "Q2"
            elif month <= 9:
                quarter = "Q3"
            else:
                quarter = "Q4"

            plan["schedule"][quarter]["audits"].append({
                "control_id": control_id,
                "control_name": control_data.get("name", "Unknown"),
                "risk_level": risk,
                "target_date": date,
            })

    # Sort audits within each quarter
    for quarter in plan["schedule"]:
        plan["schedule"][quarter]["audits"].sort(
            key=lambda x: (
                {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(x["risk_level"], 4),
                x["target_date"]
            )
        )

    # Calculate summary statistics
    risk_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    total_audits = 0
    for control_data in plan["controls"].values():
        risk_counts[control_data["risk"]] += 1
        total_audits += control_data["frequency"]

    plan["summary"] = {
        "total_controls_in_scope": len(controls),
        "total_audits_planned": total_audits,
        "risk_distribution": risk_counts,
        "audits_per_quarter": {
            q: len(plan["schedule"][q]["audits"])
            for q in plan["schedule"]
        },
    }

    return plan
def format_markdown(plan: Dict[str, Any]) -> str:
    """Format audit plan as markdown."""
    lines = [
        f"# ISMS Audit Plan {plan['metadata']['year']}",
        f"",
        f"**Generated:** {plan['metadata']['generated'][:10]}",
        f"**Methodology:** {plan['metadata']['methodology']}",
        f"",
        f"## Summary",
        f"",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Controls in Scope | {plan['summary']['total_controls_in_scope']} |",
        f"| Total Audits Planned | {plan['summary']['total_audits_planned']} |",
        f"| Critical Risk Controls | {plan['summary']['risk_distribution']['critical']} |",
        f"| High Risk Controls | {plan['summary']['risk_distribution']['high']} |",
        f"| Medium Risk Controls | {plan['summary']['risk_distribution']['medium']} |",
        f"",
    ]

    for quarter, data in plan["schedule"].items():
        lines.extend([
            f"## {quarter}: {data['month']}",
            f"",
            f"| Control | Name | Risk | Target Date |",
            f"|---------|------|------|-------------|",
        ])
        for audit in data["audits"]:
            lines.append(
                f"| {audit['control_id']} | {audit['control_name']} | "
                f"{audit['risk_level'].capitalize()} | {audit['target_date']} |"
            )
        lines.append("")

    lines.extend([
        f"## Risk-Based Audit Frequency",
        f"",
        f"| Risk Level | Audit Frequency |",
        f"|------------|-----------------|",
        f"| Critical | Quarterly (4x/year) |",
        f"| High | Semi-Annual (2x/year) |",
        f"| Medium | Annual (1x/year) |",
        f"| Low | Annual (1x/year) |",
    ])

    return "\n".join(lines)
