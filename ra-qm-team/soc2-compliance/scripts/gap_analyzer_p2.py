# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from gap_analyzer_base import *  # noqa: F403,E402
# fmt: off
from gap_analyzer_p1 import REQUIRED_TSC  # noqa: E402,E501
# fmt: on


def detect_categories(controls: List[Dict[str, Any]]) -> List[str]:
    """Detect which TSC categories are represented in the controls."""
    tsc_values = set()
    for ctrl in controls:
        tsc = ctrl.get("tsc_criteria", "")
        if tsc:
            tsc_values.add(tsc)

    categories = set()
    for cat, criteria in REQUIRED_TSC.items():
        for tsc_id in criteria:
            if tsc_id in tsc_values:
                categories.add(cat)
                break

    # Always include security as it's required
    categories.add("security")
    return sorted(categories)
def analyze_coverage(
    controls: List[Dict[str, Any]], categories: List[str]
) -> Tuple[List[Dict], List[Dict], List[Dict]]:
    """Analyze TSC coverage and identify gaps."""
    # Map existing controls by TSC criteria
    covered_tsc = {}
    for ctrl in controls:
        tsc = ctrl.get("tsc_criteria", "")
        if tsc:
            if tsc not in covered_tsc:
                covered_tsc[tsc] = []
            covered_tsc[tsc].append(ctrl)

    gaps = []
    partial = []
    covered = []

    for cat in categories:
        if cat not in REQUIRED_TSC:
            continue
        for tsc_id, tsc_desc in REQUIRED_TSC[cat].items():
            if tsc_id not in covered_tsc:
                gaps.append(
                    {
                        "tsc_criteria": tsc_id,
                        "description": tsc_desc,
                        "category": cat,
                        "gap_type": "missing",
                        "severity": "critical" if cat == "security" else "high",
                        "remediation": f"Implement control(s) addressing {tsc_id}: {tsc_desc}",
                    }
                )
            else:
                ctrls = covered_tsc[tsc_id]
                # Check for partial implementation
                has_issues = False
                for ctrl in ctrls:
                    status = ctrl.get("status", "").lower()
                    if status in ("not started", "not_started", ""):
                        has_issues = True
                    owner = ctrl.get("owner", "TBD")
                    if owner in ("TBD", "", "N/A"):
                        has_issues = True

                if has_issues:
                    partial.append(
                        {
                            "tsc_criteria": tsc_id,
                            "description": tsc_desc,
                            "category": cat,
                            "gap_type": "partial",
                            "severity": "medium",
                            "controls": [c.get("control_id", "N/A") for c in ctrls],
                            "remediation": f"Complete implementation and assign owners for {tsc_id} controls",
                        }
                    )
                else:
                    covered.append(
                        {
                            "tsc_criteria": tsc_id,
                            "description": tsc_desc,
                            "category": cat,
                            "controls": [c.get("control_id", "N/A") for c in ctrls],
                        }
                    )

    return gaps, partial, covered
