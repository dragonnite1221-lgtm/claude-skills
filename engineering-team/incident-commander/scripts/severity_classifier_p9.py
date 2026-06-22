# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from severity_classifier_base import *  # noqa: F403,E402
# fmt: off
from severity_classifier_p1 import SeverityLevel  # noqa: E402,E501
from severity_classifier_p2 import ActionPlan, EscalationPath, SLAImpact, SeverityScore  # noqa: E402,E501
# fmt: on


def format_json(
    incident: Dict,
    severity_score: SeverityScore,
    escalation: EscalationPath,
    action_plan: ActionPlan,
    sla_impact: SLAImpact,
) -> str:
    """Render a machine-readable JSON report."""
    report = {
        "classification_timestamp": datetime.now(timezone.utc).isoformat(),
        "incident": incident,
        "severity": asdict(severity_score),
        "severity_definition": SeverityLevel.get_definition(severity_score.severity_level),
        "escalation": asdict(escalation),
        "action_plan": asdict(action_plan),
        "sla_impact": asdict(sla_impact),
    }
    return json.dumps(report, indent=2, default=str)
