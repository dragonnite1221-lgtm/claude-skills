# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from compliance_checker_base import *  # noqa: F403,E402
# fmt: off
from compliance_checker_p1 import ISO27001_CONTROLS, REMEDIATION_GUIDANCE, get_control_status  # noqa: E402,E501
# fmt: on


def check_compliance(
    standard: str,
    controls_data: Optional[Dict] = None,
    domains: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Check compliance against standard controls."""
    if standard not in ["iso27001", "iso27002"]:
        print(f"Error: Unsupported standard: {standard}", file=sys.stderr)
        sys.exit(1)

    results = {
        "standard": standard,
        "timestamp": datetime.now().isoformat(),
        "domains": {},
        "summary": {
            "total_controls": 0,
            "implemented": 0,
            "partial": 0,
            "not_implemented": 0,
        },
        "findings": [],
    }

    for domain_key, domain_data in ISO27001_CONTROLS.items():
        if domains and domain_key not in domains:
            continue

        domain_results = {
            "name": domain_data["name"],
            "controls": [],
            "implemented": 0,
            "partial": 0,
            "not_implemented": 0,
        }

        for control in domain_data["controls"]:
            status = get_control_status(control["id"], controls_data)

            control_result = {
                "id": control["id"],
                "name": control["name"],
                "priority": control["priority"],
                "status": status,
            }

            domain_results["controls"].append(control_result)
            results["summary"]["total_controls"] += 1

            if status == "implemented":
                domain_results["implemented"] += 1
                results["summary"]["implemented"] += 1
            elif status == "partial":
                domain_results["partial"] += 1
                results["summary"]["partial"] += 1
            else:
                domain_results["not_implemented"] += 1
                results["summary"]["not_implemented"] += 1

                # Add to findings if high priority
                if control["priority"] in ["critical", "high"]:
                    results["findings"].append({
                        "control_id": control["id"],
                        "control_name": control["name"],
                        "priority": control["priority"],
                        "status": status,
                        "remediation": REMEDIATION_GUIDANCE.get(
                            control["id"],
                            "Implement control per ISO 27001 requirements"
                        ),
                    })

        results["domains"][domain_key] = domain_results

    # Calculate compliance percentage
    total = results["summary"]["total_controls"]
    implemented = results["summary"]["implemented"]
    partial = results["summary"]["partial"]
    results["summary"]["compliance_percentage"] = round(
        ((implemented + partial * 0.5) / total) * 100, 1
    ) if total > 0 else 0

    return results
def generate_gap_analysis(results: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate gap analysis with prioritized recommendations."""
    gaps = []

    for finding in results["findings"]:
        gap = {
            "control_id": finding["control_id"],
            "control_name": finding["control_name"],
            "current_status": finding["status"],
            "priority": finding["priority"],
            "remediation": finding["remediation"],
            "effort": "medium" if finding["priority"] == "high" else "high",
            "timeline": "30 days" if finding["priority"] == "critical" else "90 days",
        }
        gaps.append(gap)

    # Sort by priority
    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    gaps.sort(key=lambda x: priority_order.get(x["priority"], 99))

    return gaps
