# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from workflow_validator_base import *  # noqa: F403,E402


def check_missing_transitions(
    states: List[str],
    transitions: List[Dict[str, str]],
) -> List[Dict[str, str]]:
    """Check for states referenced in transitions but not defined."""
    findings = []
    defined_states = {s.lower() for s in states}

    for t in transitions:
        from_state = t.get("from", "").lower()
        to_state = t.get("to", "").lower()

        if from_state and from_state not in defined_states:
            findings.append({
                "rule": "undefined_state_reference",
                "severity": "error",
                "message": f"Transition references undefined source state '{t.get('from', '')}'.",
            })

        if to_state and to_state not in defined_states:
            findings.append({
                "rule": "undefined_state_reference",
                "severity": "error",
                "message": f"Transition references undefined target state '{t.get('to', '')}'.",
            })

    return findings
def check_circular_paths(
    states: List[str],
    transitions: List[Dict[str, str]],
    terminal_states: Set[str],
) -> List[Dict[str, str]]:
    """Detect circular paths that have no exit to a terminal state."""
    findings = []

    # Build adjacency list
    adjacency = {}
    for state in states:
        adjacency[state.lower()] = set()
    for t in transitions:
        from_state = t.get("from", "").lower()
        to_state = t.get("to", "").lower()
        if from_state in adjacency:
            adjacency[from_state].add(to_state)

    # Find strongly connected components using iterative DFS
    def can_reach_terminal(start: str) -> bool:
        visited = set()
        stack = [start]
        while stack:
            node = stack.pop()
            if node in terminal_states:
                return True
            if node in visited:
                continue
            visited.add(node)
            for neighbor in adjacency.get(node, set()):
                stack.append(neighbor)
        return False

    # Check each non-terminal state
    for state in states:
        state_lower = state.lower()
        if state_lower not in terminal_states:
            if not can_reach_terminal(state_lower):
                findings.append({
                    "rule": "circular_no_exit",
                    "severity": "error",
                    "message": f"State '{state}' cannot reach any terminal state. "
                               f"Issues entering this state will never be resolved.",
                })

    return findings
def check_self_transitions(transitions: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Check for transitions that go from a state to itself."""
    findings = []
    for t in transitions:
        if t.get("from", "").lower() == t.get("to", "").lower():
            findings.append({
                "rule": "self_transition",
                "severity": "info",
                "message": f"State '{t.get('from', '')}' has a self-transition '{t.get('name', '')}'. "
                           f"Ensure this is intentional (e.g., for triggering automation).",
            })
    return findings
