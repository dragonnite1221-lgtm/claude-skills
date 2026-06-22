# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from severity_classifier_base import *  # noqa: F403,E402
# fmt: off
from severity_classifier_p1 import SeverityLevel  # noqa: E402,E501
# fmt: on


SLA_TIERS: Dict[str, Dict[str, Any]] = {
    "SEV1": {
        "target_resolution_hours": 1,
        "target_response_minutes": 5,
        "sla_percentage": 99.95,
        "monthly_error_budget_minutes": 21.6,
    },
    "SEV2": {
        "target_resolution_hours": 4,
        "target_response_minutes": 15,
        "sla_percentage": 99.9,
        "monthly_error_budget_minutes": 43.2,
    },
    "SEV3": {
        "target_resolution_hours": 24,
        "target_response_minutes": 60,
        "sla_percentage": 99.5,
        "monthly_error_budget_minutes": 216.0,
    },
    "SEV4": {
        "target_resolution_hours": 72,
        "target_response_minutes": 480,
        "sla_percentage": 99.0,
        "monthly_error_budget_minutes": 432.0,
    },
}
ESCALATION_TEMPLATES: Dict[str, Dict[str, Any]] = {
    "SEV1": {
        "initial_notify": ["on-call-primary", "on-call-secondary", "engineering-manager"],
        "escalate_after_minutes": 15,
        "escalate_to": ["vp-engineering", "cto"],
        "bridge_required": True,
        "status_page_update": True,
        "customer_comms": True,
    },
    "SEV2": {
        "initial_notify": ["on-call-primary", "on-call-secondary"],
        "escalate_after_minutes": 30,
        "escalate_to": ["engineering-manager"],
        "bridge_required": True,
        "status_page_update": True,
        "customer_comms": False,
    },
    "SEV3": {
        "initial_notify": ["on-call-primary"],
        "escalate_after_minutes": 120,
        "escalate_to": ["on-call-secondary"],
        "bridge_required": False,
        "status_page_update": False,
        "customer_comms": False,
    },
    "SEV4": {
        "initial_notify": ["on-call-primary"],
        "escalate_after_minutes": 480,
        "escalate_to": [],
        "bridge_required": False,
        "status_page_update": False,
        "customer_comms": False,
    },
}
@dataclass
class ImpactAssessment:
    """Parsed and normalised impact data from incident input."""

    revenue_impact: str = "none"
    affected_users_percentage: float = 0.0
    affected_regions: List[str] = field(default_factory=list)
    data_integrity_risk: bool = False
    security_breach: bool = False
    customer_facing: bool = False
    degradation_type: str = "none"
    workaround_available: bool = True
@dataclass
class SeverityScore:
    """Multi-dimensional scoring result with per-dimension breakdown."""

    composite_score: float = 0.0
    severity_level: str = SeverityLevel.SEV4
    dimensions: Dict[str, float] = field(default_factory=dict)
    weighted_dimensions: Dict[str, float] = field(default_factory=dict)
    contributing_factors: List[str] = field(default_factory=list)
    auto_escalate_reasons: List[str] = field(default_factory=list)
@dataclass
class EscalationPath:
    """Generated escalation routing and notification schedule."""

    severity_level: str = SeverityLevel.SEV4
    immediate_notify: List[str] = field(default_factory=list)
    escalation_chain: List[Dict[str, Any]] = field(default_factory=list)
    cross_team_notify: List[str] = field(default_factory=list)
    war_room_required: bool = False
    bridge_link: str = ""
    status_page_update: bool = False
    customer_comms_required: bool = False
    suggested_smes: List[str] = field(default_factory=list)
@dataclass
class ActionPlan:
    """Recommended immediate actions checklist for the incident."""

    severity_level: str = SeverityLevel.SEV4
    immediate_actions: List[str] = field(default_factory=list)
    diagnostic_steps: List[str] = field(default_factory=list)
    communication_actions: List[str] = field(default_factory=list)
    rollback_assessment: Dict[str, Any] = field(default_factory=dict)
@dataclass
class SLAImpact:
    """SLA breach risk and error-budget assessment."""

    severity_level: str = SeverityLevel.SEV4
    sla_tier: Dict[str, Any] = field(default_factory=dict)
    breach_risk: str = "low"
    error_budget_impact_minutes: float = 0.0
    remaining_budget_percentage: float = 100.0
    estimated_time_to_breach_minutes: float = 0.0
    recommendations: List[str] = field(default_factory=list)
