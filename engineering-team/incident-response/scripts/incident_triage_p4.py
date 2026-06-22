# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from incident_triage_base import *  # noqa: F403,E402
# fmt: off
from incident_triage_p1 import INCIDENT_TAXONOMY  # noqa: E402,E501
from incident_triage_p2 import ESCALATION_ROUTING, FALSE_POSITIVE_INDICATORS, SEV_ESCALATION_TRIGGERS  # noqa: E402,E501
from incident_triage_p3 import _flatten_to_string, _get_synonyms  # noqa: E402,E501
# fmt: on


def classify_incident(fact: dict) -> Tuple[str, float]:
    """
    Classify incident type from event fields.

    Performs keyword matching against INCIDENT_TAXONOMY keys and the
    flattened string representation of raw_payload content.

    Returns:
        (incident_type, confidence) where confidence is 0.0–1.0.
        Returns ("unknown", 0.0) when no match is found.
    """
    # Build a single searchable string from the fact
    searchable = _flatten_to_string(fact).lower()

    scores: Dict[str, int] = {}

    for incident_type in INCIDENT_TAXONOMY:
        # The incident type slug itself is a keyword
        slug_words = incident_type.replace("_", " ").split()
        score = 0
        for word in slug_words:
            if word in searchable:
                score += 2  # direct slug match carries more weight

        # Additional keyword synonyms per type
        synonyms = _get_synonyms(incident_type)
        for syn in synonyms:
            if syn in searchable:
                score += 1

        if score > 0:
            scores[incident_type] = score

    if not scores:
        # Last resort: check explicit event_type field
        event_type = str(fact.get("event_type", "")).lower().replace(" ", "_").replace("-", "_")
        if event_type in INCIDENT_TAXONOMY:
            return event_type, 0.6
        return "unknown", 0.0

    best_type = max(scores, key=lambda k: scores[k])
    max_score = scores[best_type]

    # Normalise confidence: cap at 1.0, scale by how much the best
    # outscores alternatives
    total_score = sum(scores.values()) or 1
    raw_confidence = max_score / total_score
    # Boost if event_type field matches
    event_type = str(fact.get("event_type", "")).lower().replace(" ", "_").replace("-", "_")
    if event_type == best_type:
        raw_confidence = min(1.0, raw_confidence + 0.25)

    confidence = round(min(1.0, raw_confidence + 0.1 * min(max_score, 5)), 2)
    return best_type, confidence
def check_false_positives(fact: dict) -> List[str]:
    """
    Check fact fields against FALSE_POSITIVE_INDICATORS pattern lists.

    Returns a list of triggered false positive indicator names.
    """
    searchable = _flatten_to_string(fact).lower()
    triggered: List[str] = []

    for indicator in FALSE_POSITIVE_INDICATORS:
        for pattern in indicator["patterns"]:
            if pattern.lower() in searchable:
                triggered.append(indicator["name"])
                break  # one match per indicator is enough

    return triggered
def get_escalation_path(incident_type: str, severity: str) -> dict:
    """
    Return escalation routing for a given incident type and severity level.

    Falls back to sev4 routing if severity is not recognised.
    """
    sev_key = severity.lower()
    routing = ESCALATION_ROUTING.get(sev_key, ESCALATION_ROUTING["sev4"]).copy()

    # Augment with taxonomy SLA if available
    taxonomy = INCIDENT_TAXONOMY.get(incident_type, {})
    routing["incident_type"] = incident_type
    routing["severity"] = sev_key
    routing["response_sla_minutes"] = taxonomy.get("response_sla_minutes", 1440)
    routing["mitre_technique"] = taxonomy.get("mitre", "N/A")

    return routing
def check_sev_escalation_triggers(fact: dict) -> Optional[str]:
    """
    Scan fact fields for any SEV escalation trigger indicators.

    Returns the escalation target (e.g. 'sev1') if a trigger fires,
    or None if no triggers are present.
    """
    searchable = _flatten_to_string(fact).lower()
    # Also inspect a flat list of explicit indicator flags
    explicit_indicators: List[str] = []
    if isinstance(fact.get("indicators"), list):
        explicit_indicators = [str(i).lower() for i in fact["indicators"]]
    if isinstance(fact.get("escalation_triggers"), list):
        explicit_indicators += [str(i).lower() for i in fact["escalation_triggers"]]

    for trigger in SEV_ESCALATION_TRIGGERS:
        indicator_key = trigger["indicator"].replace("_", " ")
        indicator_raw = trigger["indicator"].lower()

        if (
            indicator_key in searchable
            or indicator_raw in searchable
            or indicator_raw in explicit_indicators
        ):
            return trigger["escalate_to"]

    return None
_SEV_ORDER = {"sev1": 1, "sev2": 2, "sev3": 3, "sev4": 4}
def _sev_to_int(sev: str) -> int:
    return _SEV_ORDER.get(sev.lower(), 4)
def _int_to_sev(n: int) -> str:
    return {1: "sev1", 2: "sev2", 3: "sev3", 4: "sev4"}.get(n, "sev4")
def _escalate_sev(current: str, target: str) -> str:
    """Return the higher severity (lower SEV number)."""
    return _int_to_sev(min(_sev_to_int(current), _sev_to_int(target)))
