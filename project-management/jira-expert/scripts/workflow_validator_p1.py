# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from workflow_validator_base import *  # noqa: F403,E402


MAX_RECOMMENDED_STATES = 10
REQUIRED_TERMINAL_STATES = {"done", "closed", "resolved", "completed"}
SEVERITY_WEIGHTS = {
    "error": 20,
    "warning": 10,
    "info": 3,
}
def check_state_count(states: List[str]) -> List[Dict[str, str]]:
    """Check if the workflow has too many states."""
    findings = []
    count = len(states)

    if count > MAX_RECOMMENDED_STATES:
        findings.append({
            "rule": "state_count",
            "severity": "warning",
            "message": f"Workflow has {count} states (recommended max: {MAX_RECOMMENDED_STATES}). "
                       f"Complex workflows slow teams down and increase error rates.",
        })
    elif count < 2:
        findings.append({
            "rule": "state_count",
            "severity": "error",
            "message": f"Workflow has only {count} state(s). A minimum of 2 states is required.",
        })

    if count > 15:
        findings[-1]["severity"] = "error"

    return findings
def check_dead_end_states(
    states: List[str],
    transitions: List[Dict[str, str]],
    terminal_states: Set[str],
) -> List[Dict[str, str]]:
    """Find states with no outgoing transitions that are not terminal."""
    findings = []
    outgoing = set()
    for t in transitions:
        outgoing.add(t.get("from", "").lower())

    for state in states:
        state_lower = state.lower()
        if state_lower not in outgoing and state_lower not in terminal_states:
            findings.append({
                "rule": "dead_end_state",
                "severity": "error",
                "message": f"State '{state}' has no outgoing transitions and is not a terminal state. "
                           f"Issues will get stuck here.",
            })

    return findings
def check_orphan_states(
    states: List[str],
    transitions: List[Dict[str, str]],
    initial_state: Optional[str],
) -> List[Dict[str, str]]:
    """Find states with no incoming transitions (except the initial state)."""
    findings = []
    incoming = set()
    for t in transitions:
        incoming.add(t.get("to", "").lower())

    initial_lower = (initial_state or "").lower()

    for state in states:
        state_lower = state.lower()
        if state_lower not in incoming and state_lower != initial_lower:
            findings.append({
                "rule": "orphan_state",
                "severity": "warning",
                "message": f"State '{state}' has no incoming transitions and is not the initial state. "
                           f"This state may be unreachable.",
            })

    return findings
def check_missing_terminal_state(states: List[str]) -> List[Dict[str, str]]:
    """Check that at least one terminal/done state exists."""
    findings = []
    states_lower = {s.lower() for s in states}

    has_terminal = bool(states_lower & REQUIRED_TERMINAL_STATES)
    if not has_terminal:
        findings.append({
            "rule": "missing_terminal_state",
            "severity": "error",
            "message": f"No terminal state found. Expected one of: {', '.join(sorted(REQUIRED_TERMINAL_STATES))}. "
                       f"Issues cannot be marked as complete.",
        })

    return findings
def check_duplicate_transition_names(
    transitions: List[Dict[str, str]],
) -> List[Dict[str, str]]:
    """Check for duplicate transition names from the same state."""
    findings = []
    seen = {}

    for t in transitions:
        name = t.get("name", "").lower()
        from_state = t.get("from", "").lower()
        key = (from_state, name)

        if key in seen:
            findings.append({
                "rule": "duplicate_transition",
                "severity": "warning",
                "message": f"Duplicate transition name '{t.get('name', '')}' from state '{t.get('from', '')}'. "
                           f"This can confuse users selecting transitions.",
            })
        else:
            seen[key] = True

    return findings
