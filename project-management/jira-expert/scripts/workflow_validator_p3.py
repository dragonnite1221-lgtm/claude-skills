# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from workflow_validator_base import *  # noqa: F403,E402
# fmt: off
from workflow_validator_p1 import REQUIRED_TERMINAL_STATES, SEVERITY_WEIGHTS, check_dead_end_states, check_duplicate_transition_names, check_missing_terminal_state, check_orphan_states, check_state_count  # noqa: E402,E501
from workflow_validator_p2 import check_circular_paths, check_missing_transitions, check_self_transitions  # noqa: E402,E501
# fmt: on


def validate_workflow(data: Dict[str, Any]) -> Dict[str, Any]:
    """Run all validations on a workflow definition."""
    states = data.get("states", [])
    transitions = data.get("transitions", [])
    initial_state = data.get("initial_state", states[0] if states else None)

    if not states:
        return {
            "health_score": 0,
            "grade": "invalid",
            "findings": [{"rule": "no_states", "severity": "error", "message": "No states defined in workflow"}],
            "summary": {"errors": 1, "warnings": 0, "info": 0},
        }

    # Determine terminal states
    states_lower = {s.lower() for s in states}
    terminal_states = states_lower & REQUIRED_TERMINAL_STATES

    # Custom terminal states from input
    custom_terminals = data.get("terminal_states", [])
    for ct in custom_terminals:
        terminal_states.add(ct.lower())

    # Run all checks
    all_findings = []
    all_findings.extend(check_state_count(states))
    all_findings.extend(check_dead_end_states(states, transitions, terminal_states))
    all_findings.extend(check_orphan_states(states, transitions, initial_state))
    all_findings.extend(check_missing_terminal_state(states))
    all_findings.extend(check_duplicate_transition_names(transitions))
    all_findings.extend(check_missing_transitions(states, transitions))
    all_findings.extend(check_circular_paths(states, transitions, terminal_states))
    all_findings.extend(check_self_transitions(transitions))

    # Calculate health score
    summary = {"errors": 0, "warnings": 0, "info": 0}
    penalty = 0
    for finding in all_findings:
        severity = finding["severity"]
        summary[severity] = summary.get(severity, 0) + 1
        penalty += SEVERITY_WEIGHTS.get(severity, 0)

    health_score = max(0, 100 - penalty)

    if health_score >= 90:
        grade = "excellent"
    elif health_score >= 75:
        grade = "good"
    elif health_score >= 55:
        grade = "fair"
    else:
        grade = "poor"

    return {
        "health_score": health_score,
        "grade": grade,
        "findings": all_findings,
        "summary": summary,
        "workflow_info": {
            "state_count": len(states),
            "transition_count": len(transitions),
            "initial_state": initial_state,
            "terminal_states": sorted(terminal_states),
        },
    }
def format_text_output(result: Dict[str, Any]) -> str:
    """Format results as readable text report."""
    lines = []
    lines.append("=" * 60)
    lines.append("WORKFLOW VALIDATION REPORT")
    lines.append("=" * 60)
    lines.append("")

    # Health summary
    lines.append("HEALTH SUMMARY")
    lines.append("-" * 30)
    lines.append(f"Health Score: {result['health_score']}/100")
    lines.append(f"Grade: {result['grade'].title()}")
    lines.append("")

    # Workflow info
    info = result.get("workflow_info", {})
    if info:
        lines.append("WORKFLOW INFO")
        lines.append("-" * 30)
        lines.append(f"States: {info.get('state_count', 0)}")
        lines.append(f"Transitions: {info.get('transition_count', 0)}")
        lines.append(f"Initial State: {info.get('initial_state', 'N/A')}")
        lines.append(f"Terminal States: {', '.join(info.get('terminal_states', []))}")
        lines.append("")

    # Summary
    summary = result.get("summary", {})
    lines.append("FINDINGS SUMMARY")
    lines.append("-" * 30)
    lines.append(f"Errors: {summary.get('errors', 0)}")
    lines.append(f"Warnings: {summary.get('warnings', 0)}")
    lines.append(f"Info: {summary.get('info', 0)}")
    lines.append("")

    # Detailed findings
    findings = result.get("findings", [])
    if findings:
        lines.append("DETAILED FINDINGS")
        lines.append("-" * 30)
        for i, finding in enumerate(findings, 1):
            severity = finding["severity"].upper()
            lines.append(f"{i}. [{severity}] {finding['message']}")
            lines.append(f"   Rule: {finding['rule']}")
            lines.append("")
    else:
        lines.append("No issues found. Workflow looks healthy!")

    return "\n".join(lines)
def format_json_output(result: Dict[str, Any]) -> Dict[str, Any]:
    """Format results as JSON."""
    return result
