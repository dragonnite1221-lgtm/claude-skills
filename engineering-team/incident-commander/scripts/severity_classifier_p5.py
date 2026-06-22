# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from severity_classifier_base import *  # noqa: F403,E402
# fmt: off
from severity_classifier_p1 import SeverityLevel  # noqa: E402,E501
from severity_classifier_p2 import ESCALATION_TEMPLATES, EscalationPath, SeverityScore  # noqa: E402,E501
# fmt: on


def build_escalation_path(
    severity_score: SeverityScore,
    signals: Dict,
    context: Dict,
) -> EscalationPath:
    """Generate the escalation routing based on severity and context."""
    level = severity_score.severity_level
    template = ESCALATION_TEMPLATES.get(level, ESCALATION_TEMPLATES["SEV4"])

    on_call = context.get("on_call", {})
    primary = on_call.get("primary", "on-call-primary@company.com")
    secondary = on_call.get("secondary", "on-call-secondary@company.com")

    immediate: List[str] = []
    for role in template["initial_notify"]:
        if role == "on-call-primary":
            immediate.append(primary)
        elif role == "on-call-secondary":
            immediate.append(secondary)
        else:
            immediate.append(role)

    chain: List[Dict[str, Any]] = []
    if template["escalate_to"]:
        chain.append({
            "trigger_after_minutes": template["escalate_after_minutes"],
            "notify": template["escalate_to"],
            "reason": f"No resolution within {template['escalate_after_minutes']} minutes",
        })

    sev_def = SeverityLevel.get_definition(level)
    if sev_def.get("executive_notify"):
        chain.append({
            "trigger_after_minutes": 15,
            "notify": ["vp-engineering", "cto"],
            "reason": "SEV1 executive notification policy",
        })

    cross_team: List[str] = []
    dependent_services = signals.get("dependent_services", [])
    for svc in dependent_services:
        cross_team.append(f"{svc}-team")

    suggested_smes: List[str] = []
    affected_endpoints = signals.get("affected_endpoints", [])
    if affected_endpoints:
        suggested_smes.append(f"API owner for: {', '.join(affected_endpoints[:3])}")
    if dependent_services:
        suggested_smes.append(f"Service owners: {', '.join(dependent_services[:3])}")

    ongoing = context.get("ongoing_incidents", [])
    if ongoing:
        suggested_smes.append("Incident coordinator (multiple active incidents)")

    bridge_link = ""
    if template["bridge_required"]:
        bridge_link = f"https://bridge.company.com/incident-{level.lower()}"

    return EscalationPath(
        severity_level=level,
        immediate_notify=immediate,
        escalation_chain=chain,
        cross_team_notify=cross_team,
        war_room_required=template["bridge_required"],
        bridge_link=bridge_link,
        status_page_update=template["status_page_update"],
        customer_comms_required=template.get("customer_comms", False),
        suggested_smes=suggested_smes,
    )
