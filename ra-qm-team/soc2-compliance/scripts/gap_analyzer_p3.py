# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from gap_analyzer_base import *  # noqa: F403,E402
# fmt: off
from gap_analyzer_p1 import REQUIRED_TSC  # noqa: E402,E501
# fmt: on


def analyze_type2_gaps(controls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Additional gap analysis for Type II operating effectiveness."""
    type2_gaps = []

    for ctrl in controls:
        ctrl_id = ctrl.get("control_id", "N/A")
        issues = []

        # Check for evidence date coverage
        evidence_date = ctrl.get("evidence_date", "")
        if not evidence_date:
            issues.append(
                {
                    "check": "evidence_period",
                    "severity": "critical",
                    "detail": "No evidence date recorded",
                }
            )

        # Check owner assignment
        owner = ctrl.get("owner", "TBD")
        if owner in ("TBD", "", "N/A"):
            issues.append(
                {
                    "check": "owner_accountability",
                    "severity": "medium",
                    "detail": "No control owner assigned",
                }
            )

        # Check status for operating evidence
        status = ctrl.get("status", "").lower()
        if status not in ("collected", "complete", "done"):
            issues.append(
                {
                    "check": "operating_consistency",
                    "severity": "critical",
                    "detail": f"Control status is '{ctrl.get('status', 'Not Started')}' — operating evidence needed",
                }
            )

        # Check frequency is defined
        frequency = ctrl.get("frequency", "")
        if not frequency:
            issues.append(
                {
                    "check": "frequency_adherence",
                    "severity": "critical",
                    "detail": "No control frequency defined",
                }
            )

        if issues:
            type2_gaps.append(
                {
                    "control_id": ctrl_id,
                    "tsc_criteria": ctrl.get("tsc_criteria", "N/A"),
                    "description": ctrl.get("description", "N/A"),
                    "issues": issues,
                }
            )

    return type2_gaps
def build_report(
    controls: List[Dict[str, Any]],
    audit_type: str,
    categories: List[str],
    gaps: List[Dict],
    partial: List[Dict],
    covered: List[Dict],
    type2_gaps: List[Dict],
) -> Dict[str, Any]:
    """Build the complete gap analysis report."""
    total_criteria = sum(
        len(REQUIRED_TSC[c]) for c in categories if c in REQUIRED_TSC
    )
    covered_count = len(covered)
    gap_count = len(gaps)
    partial_count = len(partial)

    coverage_pct = (
        round(covered_count / total_criteria * 100, 1) if total_criteria > 0 else 0
    )
    critical_gaps = len([g for g in gaps if g.get("severity") == "critical"])

    if coverage_pct >= 90 and critical_gaps == 0:
        readiness = "Ready"
    elif coverage_pct >= 75:
        readiness = "Near Ready — address gaps before audit"
    elif coverage_pct >= 50:
        readiness = "Significant work needed"
    else:
        readiness = "Not ready — major build-out required"

    report = {
        "report_metadata": {
            "audit_type": audit_type,
            "categories_assessed": categories,
            "report_date": datetime.now().strftime("%Y-%m-%d"),
            "total_controls_assessed": len(controls),
        },
        "coverage_summary": {
            "total_criteria": total_criteria,
            "covered": covered_count,
            "partially_covered": partial_count,
            "missing": gap_count,
            "coverage_percentage": coverage_pct,
            "critical_gaps": critical_gaps,
            "readiness_assessment": readiness,
        },
        "gaps": gaps,
        "partial_implementations": partial,
        "covered_criteria": covered,
    }

    if audit_type == "type2":
        type2_issue_count = sum(len(g["issues"]) for g in type2_gaps)
        report["type2_operating_gaps"] = {
            "controls_with_issues": len(type2_gaps),
            "total_issues": type2_issue_count,
            "details": type2_gaps,
        }

    return report
