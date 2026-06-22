# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from root_cause_analyzer_base import *  # noqa: F403,E402
from root_cause_analyzer_p0 import RootCauseAnalysis  # noqa: F401,E501


def format_rca_text(rca: RootCauseAnalysis) -> str:
    """Format RCA report as text."""
    lines = [
        "=" * 70,
        "ROOT CAUSE ANALYSIS REPORT",
        "=" * 70,
        f"Investigation ID: {rca.investigation_id}",
        f"Analysis Method: {rca.analysis_method}",
        f"Confidence Level: {rca.confidence_level:.0%}",
        "",
        "PROBLEM STATEMENT",
        "-" * 40,
        f"  {rca.problem_statement}",
        "",
        "ROOT CAUSES IDENTIFIED",
        "-" * 40,
    ]

    for rc in rca.root_causes:
        lines.extend([
            f"",
            f"  [{rc.cause_id}] {rc.description}",
            f"  Category: {rc.category}",
            f"  Systemic: {'Yes' if rc.systemic else 'No'}",
        ])
        if rc.evidence:
            lines.append(f"  Evidence:")
            for ev in rc.evidence:
                if ev:
                    lines.append(f"    • {ev}")
        if rc.contributing_factors:
            lines.append(f"  Contributing Factors:")
            for cf in rc.contributing_factors:
                lines.append(f"    - {cf}")

    lines.extend([
        "",
        "RECOMMENDED ACTIONS",
        "-" * 40,
    ])

    for rec in rca.recommendations:
        lines.extend([
            f"",
            f"  [{rec.action_id}] {rec.action_type}: {rec.description}",
            f"  Priority: {rec.priority} | Effort: {rec.estimated_effort}",
            f"  Responsible: {rec.responsible_role}",
            f"  Effectiveness Criteria:",
        ])
        for ec in rec.effectiveness_criteria:
            lines.append(f"    ✓ {ec}")

    if "steps" in rca.analysis_details:
        lines.extend([
            "",
            "5-WHY CHAIN",
            "-" * 40,
        ])
        for step in rca.analysis_details["steps"]:
            lines.extend([
                f"",
                f"  Why {step['level']}: {step['question']}",
                f"  → {step['answer']}",
            ])
            if step.get("evidence"):
                lines.append(f"  Evidence: {step['evidence']}")

    lines.append("=" * 70)
    return "\n".join(lines)
