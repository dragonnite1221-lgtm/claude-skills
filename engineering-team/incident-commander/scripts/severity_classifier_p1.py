# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from severity_classifier_base import *  # noqa: F403,E402


class SeverityLevel:
    """Enum-like container for SEV1 through SEV4 definitions."""

    SEV1 = "SEV1"
    SEV2 = "SEV2"
    SEV3 = "SEV3"
    SEV4 = "SEV4"

    DEFINITIONS: Dict[str, Dict[str, Any]] = {
        "SEV1": {
            "label": "Critical",
            "description": (
                "Complete service outage, confirmed data loss or corruption, "
                "active security breach, or more than 50% of users affected."
            ),
            "score_threshold": 0.75,
            "response_time_minutes": 5,
            "update_cadence_minutes": 15,
            "executive_notify": True,
            "war_room": True,
        },
        "SEV2": {
            "label": "Major",
            "description": (
                "Significant service degradation, more than 25% of users "
                "affected, no viable workaround, or high revenue impact."
            ),
            "score_threshold": 0.50,
            "response_time_minutes": 15,
            "update_cadence_minutes": 30,
            "executive_notify": False,
            "war_room": True,
        },
        "SEV3": {
            "label": "Moderate",
            "description": (
                "Partial degradation with workaround available, fewer than "
                "25% of users affected, limited blast radius."
            ),
            "score_threshold": 0.25,
            "response_time_minutes": 30,
            "update_cadence_minutes": 60,
            "executive_notify": False,
            "war_room": False,
        },
        "SEV4": {
            "label": "Minor",
            "description": (
                "Cosmetic issue, low impact, minimal user effect, "
                "informational or non-urgent."
            ),
            "score_threshold": 0.0,
            "response_time_minutes": 120,
            "update_cadence_minutes": 240,
            "executive_notify": False,
            "war_room": False,
        },
    }

    @classmethod
    def from_score(cls, score: float) -> str:
        """Return the severity level string for a given composite score."""
        for level in [cls.SEV1, cls.SEV2, cls.SEV3]:
            if score >= cls.DEFINITIONS[level]["score_threshold"]:
                return level
        return cls.SEV4

    @classmethod
    def get_definition(cls, level: str) -> Dict[str, Any]:
        return cls.DEFINITIONS.get(level, cls.DEFINITIONS[cls.SEV4])
DIMENSION_WEIGHTS: Dict[str, float] = {
    "revenue_impact": 0.25,
    "user_impact_scope": 0.25,
    "data_security_risk": 0.20,
    "service_criticality": 0.15,
    "blast_radius": 0.15,
}
REVENUE_IMPACT_SCORES: Dict[str, float] = {
    "critical": 1.0,
    "high": 0.8,
    "medium": 0.5,
    "low": 0.2,
    "none": 0.0,
}
DEGRADATION_SCORES: Dict[str, float] = {
    "complete": 1.0,
    "major": 0.75,
    "partial": 0.50,
    "minor": 0.25,
    "none": 0.0,
}
ERROR_RATE_THRESHOLDS: List[Tuple[float, float]] = [
    (50.0, 1.0),
    (25.0, 0.8),
    (10.0, 0.6),
    (5.0, 0.4),
    (1.0, 0.2),
]
LATENCY_P99_THRESHOLDS_MS: List[Tuple[float, float]] = [
    (10000, 1.0),
    (5000, 0.8),
    (2000, 0.6),
    (1000, 0.4),
    (500, 0.2),
]
