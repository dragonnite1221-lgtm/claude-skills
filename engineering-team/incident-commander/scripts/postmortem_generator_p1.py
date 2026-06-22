# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from postmortem_generator_base import *  # noqa: F403,E402


VERSION = "1.0.0"
SEVERITY_ORDER = {"SEV0": 0, "SEV1": 1, "SEV2": 2, "SEV3": 3, "SEV4": 4}
FACTOR_CATEGORIES = ("process", "tooling", "human", "environment", "external")
ACTION_TYPES = ("detection", "prevention", "mitigation", "process")
PRIORITY_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3, "P4": 4}
POSTMORTEM_TARGET_HOURS = 72
BENCHMARKS = {
    "SEV0": {"mttd": 5, "mttr": 60, "mitigate": 30, "declare": 5},
    "SEV1": {"mttd": 10, "mttr": 120, "mitigate": 60, "declare": 10},
    "SEV2": {"mttd": 30, "mttr": 480, "mitigate": 120, "declare": 30},
    "SEV3": {"mttd": 60, "mttr": 1440, "mitigate": 240, "declare": 60},
    "SEV4": {"mttd": 120, "mttr": 2880, "mitigate": 480, "declare": 120},
}
CAT_TO_ACTION = {"process": "process", "tooling": "detection", "human": "prevention",
                 "environment": "mitigation", "external": "prevention"}
CAT_WEIGHT = {"process": 1.0, "tooling": 0.9, "human": 0.8, "environment": 0.7, "external": 0.6}
FACTOR_KEYWORDS = {
    "process": ["process", "procedure", "workflow", "review", "approval", "checklist",
                 "runbook", "documentation", "policy", "standard", "protocol", "canary",
                 "deployment", "rollback", "change management"],
    "tooling": ["tool", "monitor", "alert", "threshold", "automation", "test", "pipeline",
                "ci/cd", "observability", "dashboard", "logging", "infrastructure",
                "configuration", "config"],
    "human": ["training", "knowledge", "experience", "communication", "handoff", "fatigue",
              "oversight", "mistake", "error", "misunderstand", "assumption", "awareness"],
    "environment": ["load", "traffic", "scale", "capacity", "resource", "network", "hardware",
                    "region", "latency", "timeout", "connection", "performance", "spike"],
    "external": ["vendor", "third-party", "upstream", "downstream", "provider", "api",
                 "dependency", "partner", "dns", "cdn", "certificate"],
}
WHY_TEMPLATES = {
    "process": [
        "Why did this process gap exist? -> The existing process did not account for this scenario.",
        "Why was the scenario not accounted for? -> It was not identified during the last process review.",
        "Why was the process review incomplete? -> Reviews focus on known failure modes, not emerging risks.",
        "Why are emerging risks not surfaced? -> No systematic mechanism to capture lessons from near-misses.",
        "Why is there no near-miss capture mechanism? -> Incident learning is ad-hoc rather than systematic."],
    "tooling": [
        "Why did the tooling fail to catch this? -> The relevant metric was not monitored or the threshold was misconfigured.",
        "Why was the threshold misconfigured? -> It was set during initial deployment and never revisited.",
        "Why was it never revisited? -> There is no scheduled review of monitoring configurations.",
        "Why is there no scheduled review? -> Monitoring ownership is diffuse across teams.",
        "Why is ownership diffuse? -> No clear operational runbook assigns monitoring review responsibilities."],
    "human": [
        "Why did the human factor contribute? -> The individual lacked context needed to prevent the issue.",
        "Why was context lacking? -> Knowledge was siloed and not documented accessibly.",
        "Why was knowledge siloed? -> No structured onboarding or knowledge-sharing process for this area.",
        "Why is there no knowledge-sharing process? -> Team capacity has been focused on feature delivery.",
        "Why is capacity skewed toward features? -> Operational excellence is not weighted equally in planning."],
    "environment": [
        "Why did the environment cause this failure? -> System capacity was insufficient for the load pattern.",
        "Why was capacity insufficient? -> Load projections did not account for this traffic pattern.",
        "Why were projections inaccurate? -> Load testing does not replicate production-scale variability.",
        "Why doesn't load testing replicate production? -> Test environments lack realistic traffic generators.",
        "Why are traffic generators missing? -> Investment in production-like test infrastructure was deferred."],
    "external": [
        "Why did the external factor cause an incident? -> The system had a hard dependency with no fallback.",
        "Why was there no fallback? -> The integration was assumed to be highly available.",
        "Why was high availability assumed? -> SLA review of the external dependency was not performed.",
        "Why was SLA review skipped? -> No standard checklist for evaluating third-party dependencies.",
        "Why is there no evaluation checklist? -> Vendor management practices are informal and undocumented."],
}
THEME_RECS = {
    "process": ["Establish a quarterly process review cadence covering change management and deployment procedures.",
                "Implement a near-miss tracking system to surface latent risks before they become incidents.",
                "Create pre-deployment checklists that require sign-off from the service owner."],
    "tooling": ["Schedule quarterly reviews of alerting thresholds and monitoring coverage.",
                "Assign explicit monitoring ownership per service in operational runbooks.",
                "Invest in synthetic monitoring and canary analysis for critical paths."],
    "human": ["Build structured onboarding that covers incident-prone areas and past postmortems.",
              "Implement blameless knowledge-sharing sessions after each incident.",
              "Balance operational excellence work alongside feature delivery in sprint planning."],
    "environment": ["Conduct periodic capacity planning reviews using production traffic replays.",
                    "Invest in production-like load-testing infrastructure with realistic traffic profiles.",
                    "Implement auto-scaling policies with validated upper-bound thresholds."],
    "external": ["Perform formal SLA reviews for all third-party dependencies annually.",
                 "Implement circuit breakers and fallbacks for external service integrations.",
                 "Maintain a dependency registry with risk ratings and contingency plans."],
}
MISSING_ACTION_TEMPLATES = {
    "process": "Create or update runbook/checklist to prevent recurrence of this process gap",
    "detection": "Add monitoring and alerting to detect this class of issue earlier",
    "mitigation": "Implement auto-scaling or circuit-breaker to reduce blast radius",
    "prevention": "Add automated safeguards (canary deploy, load test gate) to prevent recurrence",
}
class IncidentData:
    """Parsed incident metadata."""
    def __init__(self, data: Dict[str, Any]) -> None:
        self.id: str = data.get("id", "UNKNOWN")
        self.title: str = data.get("title", "Untitled Incident")
        self.severity: str = data.get("severity", "SEV3").upper()
        self.commander: str = data.get("commander", "Unassigned")
        self.service: str = data.get("service", "unknown-service")
        self.affected_services: List[str] = data.get("affected_services", [])

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "title": self.title, "severity": self.severity,
                "commander": self.commander, "service": self.service,
                "affected_services": self.affected_services}
