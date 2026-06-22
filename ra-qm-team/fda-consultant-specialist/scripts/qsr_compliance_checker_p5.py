# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from qsr_compliance_checker_base import *  # noqa: F403,E402


def generate_gap_report(assessment_results: List[Dict]) -> Dict:
    """Generate gap analysis report."""
    gaps = []
    recommendations = []

    for section in assessment_results:
        for subsection in section["subsections"]:
            if subsection["status"] != "compliant":
                gap = {
                    "section": subsection["subsection"],
                    "title": subsection["title"],
                    "status": subsection["status"],
                    "missing_evidence": subsection["required_evidence"]
                }
                gaps.append(gap)

                if subsection["status"] == "gap":
                    recommendations.append(
                        f"{subsection['subsection']}: Create documentation for {subsection['title']}"
                    )
                else:
                    recommendations.append(
                        f"{subsection['subsection']}: Enhance documentation for {subsection['title']}"
                    )

    return {
        "total_gaps": len([g for g in gaps if g["status"] == "gap"]),
        "total_partial": len([g for g in gaps if g["status"] == "partial"]),
        "gaps": gaps,
        "priority_recommendations": recommendations[:10]  # Top 10
    }
def calculate_overall_compliance(assessment_results: List[Dict]) -> Dict:
    """Calculate overall QSR compliance score."""
    total_subsections = 0
    compliant_subsections = 0

    section_scores = {}
    for section in assessment_results:
        total_subsections += section["total_subsections"]
        compliant_subsections += section["compliant_subsections"]
        section_scores[section["section"]] = section["compliance_score"]

    overall_score = round((compliant_subsections / total_subsections) * 100, 1) if total_subsections > 0 else 0

    # Determine compliance level
    if overall_score >= 90:
        level = "HIGH"
        color = "green"
    elif overall_score >= 70:
        level = "MEDIUM"
        color = "yellow"
    elif overall_score >= 50:
        level = "LOW"
        color = "orange"
    else:
        level = "CRITICAL"
        color = "red"

    return {
        "overall_score": overall_score,
        "compliance_level": level,
        "total_subsections": total_subsections,
        "compliant_subsections": compliant_subsections,
        "section_scores": section_scores
    }
def print_text_report(result: Dict) -> None:
    """Print human-readable compliance report."""
    print("=" * 70)
    print("21 CFR PART 820 (QSR) COMPLIANCE ASSESSMENT")
    print("=" * 70)

    # Overall compliance
    overall = result["overall_compliance"]
    print(f"\nOVERALL COMPLIANCE: {overall['overall_score']}% ({overall['compliance_level']})")
    print(f"Subsections Assessed: {overall['total_subsections']}")
    print(f"Compliant/Partial: {overall['compliant_subsections']}")

    # Section summary
    print("\n--- SECTION SCORES ---")
    for section in result["assessment"]:
        status = "OK" if section["compliance_score"] >= 70 else "GAP"
        print(f"  {section['section']} {section['title']}: {section['compliance_score']}% [{status}]")

    # Gap analysis
    gap_report = result["gap_report"]
    print(f"\n--- GAP ANALYSIS ---")
    print(f"Critical Gaps: {gap_report['total_gaps']}")
    print(f"Partial Compliance: {gap_report['total_partial']}")

    if gap_report["gaps"]:
        print("\n  Gaps Identified:")
        for gap in gap_report["gaps"][:15]:  # Show top 15
            status = "GAP" if gap["status"] == "gap" else "PARTIAL"
            print(f"    [{status}] {gap['section']}: {gap['title']}")

    # Recommendations
    if gap_report["priority_recommendations"]:
        print("\n--- PRIORITY RECOMMENDATIONS ---")
        for i, rec in enumerate(gap_report["priority_recommendations"], 1):
            print(f"  {i}. {rec}")

    print("\n" + "=" * 70)
    print(f"Assessment Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 70)
