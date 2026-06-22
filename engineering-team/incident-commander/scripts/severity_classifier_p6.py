# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from severity_classifier_base import *  # noqa: F403,E402
# fmt: off
from severity_classifier_p1 import SeverityLevel  # noqa: E402,E501
from severity_classifier_p2 import ActionPlan, ImpactAssessment, SeverityScore  # noqa: E402,E501
# fmt: on


def build_action_plan(
    severity_score: SeverityScore,
    incident: Dict,
    impact: ImpactAssessment,
    signals: Dict,
    context: Dict,
) -> ActionPlan:
    """Generate the immediate action plan for the classified incident."""
    level = severity_score.severity_level
    sev_def = SeverityLevel.get_definition(level)

    # -- Immediate actions --
    immediate: List[str] = [
        f"Acknowledge incident within {sev_def['response_time_minutes']} minutes",
        "Join the war room / bridge call" if sev_def["war_room"] else "Open incident channel",
        f"Post status update every {sev_def['update_cadence_minutes']} minutes",
    ]

    if level in (SeverityLevel.SEV1, SeverityLevel.SEV2):
        immediate.append("Page secondary on-call if primary unresponsive within 5 minutes")
        immediate.append("Begin impact quantification for executive update")

    if impact.security_breach:
        immediate.insert(0, "CRITICAL: Initiate security incident response playbook")
        immediate.append("Engage security team immediately")
        immediate.append("Preserve forensic evidence -- do not restart services yet")

    if impact.data_integrity_risk:
        immediate.append("Halt writes to affected data stores if safe to do so")
        immediate.append("Begin data integrity verification")

    # -- Diagnostic steps --
    diagnostics: List[str] = [
        "Check service dashboards and recent metric trends",
        "Review application logs for error spikes",
        "Verify upstream and downstream dependency health",
    ]

    error_rate = signals.get("error_rate_percentage", 0)
    if error_rate > 10:
        diagnostics.append(f"Investigate error rate spike ({error_rate}%)")

    latency = signals.get("latency_p99_ms", 0)
    if latency > 2000:
        diagnostics.append(f"Investigate latency degradation (P99 = {latency}ms)")

    affected_endpoints = signals.get("affected_endpoints", [])
    if affected_endpoints:
        diagnostics.append(
            f"Trace requests to affected endpoints: {', '.join(affected_endpoints[:5])}"
        )

    dependent_services = signals.get("dependent_services", [])
    if dependent_services:
        diagnostics.append(
            f"Check health of dependent services: {', '.join(dependent_services)}"
        )

    # -- Communication actions --
    comms: List[str] = []
    if sev_def.get("executive_notify"):
        comms.append("Draft executive summary within 15 minutes")
    if level in (SeverityLevel.SEV1, SeverityLevel.SEV2):
        comms.append("Post initial status page update")
        comms.append("Notify customer success team for proactive outreach")
    comms.append(f"Schedule post-incident review within 48 hours")

    # -- Rollback assessment --
    recent_deploys = context.get("recent_deployments", [])
    rollback: Dict[str, Any] = {"recent_deployment_detected": False, "recommendation": ""}

    if recent_deploys:
        latest = recent_deploys[0]
        rollback["recent_deployment_detected"] = True
        rollback["service"] = latest.get("service", "unknown")
        rollback["version"] = latest.get("version", "unknown")
        rollback["deployed_at"] = latest.get("deployed_at", "unknown")

        detected_at = incident.get("detected_at", "")
        deploy_time = latest.get("deployed_at", "")
        if detected_at and deploy_time:
            try:
                det = datetime.fromisoformat(detected_at.replace("Z", "+00:00"))
                dep = datetime.fromisoformat(deploy_time.replace("Z", "+00:00"))
                delta_minutes = (det - dep).total_seconds() / 60
                rollback["minutes_since_deploy"] = round(delta_minutes, 1)
                if 0 < delta_minutes < 120:
                    rollback["recommendation"] = (
                        f"STRONG: Deployment of {latest.get('service')} v{latest.get('version')} "
                        f"occurred {round(delta_minutes)} minutes before detection. "
                        "Consider immediate rollback."
                    )
                else:
                    rollback["recommendation"] = (
                        "Recent deployment is outside the typical correlation window. "
                        "Investigate other root causes first."
                    )
            except (ValueError, TypeError):
                rollback["recommendation"] = (
                    "Unable to parse timestamps. Manually assess deployment correlation."
                )
    else:
        rollback["recommendation"] = (
            "No recent deployments detected. Focus on infrastructure and dependency investigation."
        )

    return ActionPlan(
        severity_level=level,
        immediate_actions=immediate,
        diagnostic_steps=diagnostics,
        communication_actions=comms,
        rollback_assessment=rollback,
    )
