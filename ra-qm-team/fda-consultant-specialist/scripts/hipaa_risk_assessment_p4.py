# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from hipaa_risk_assessment_base import *  # noqa: F403,E402


def generate_recommendations(assessment: Dict) -> List[str]:
    """Generate prioritized recommendations."""
    recommendations = []

    # Technical safeguards first (highest priority for software)
    for cat in assessment["categories"]:
        if cat["category"] == "technical":
            for control in cat["controls"]:
                if control["status"] == "gap":
                    recommendations.append(f"CRITICAL: Implement {control['title']} - {control['requirement']}")
                elif control["status"] == "partial":
                    recommendations.append(f"HIGH: Complete {control['title']} implementation")

    # Administrative safeguards
    for cat in assessment["categories"]:
        if cat["category"] == "administrative":
            for control in cat["controls"]:
                if control["status"] == "gap":
                    recommendations.append(f"MEDIUM: Document {control['title']} procedures")

    # Vulnerabilities
    for vuln in assessment.get("vulnerabilities", [])[:5]:
        recommendations.append(f"SECURITY: Fix {vuln['vulnerability']} in {vuln['file']}")

    return recommendations[:10]  # Top 10
def print_text_report(result: Dict) -> None:
    """Print human-readable report."""
    print("=" * 70)
    print("HIPAA SECURITY RULE COMPLIANCE ASSESSMENT")
    print("=" * 70)

    # Risk summary
    risk = result["risk_assessment"]
    print(f"\nRISK LEVEL: {risk['risk_level']}")
    print(f"Compliance Score: {risk['compliance_score']}%")
    print(f"Vulnerabilities Found: {risk['vulnerability_count']}")
    print(f"PHI Handling Detected: {'Yes' if risk['phi_handling_detected'] else 'No'}")

    # Category scores
    print("\n--- SAFEGUARD CATEGORIES ---")
    for cat in result["categories"]:
        status = "OK" if cat["score"] >= 70 else "NEEDS ATTENTION"
        print(f"  {cat['title']}: {cat['score']}% [{status}]")
        print(f"    Implemented: {cat['compliant']}, Partial: {cat['partial']}, Gaps: {cat['gaps']}")

    # Gaps
    print("\n--- COMPLIANCE GAPS ---")
    gap_count = 0
    for cat in result["categories"]:
        for control in cat["controls"]:
            if control["status"] == "gap":
                gap_count += 1
                print(f"  [{cat['category'].upper()}] {control['title']}")
                print(f"    Requirement: {control['requirement']}")
    if gap_count == 0:
        print("  No critical gaps identified")

    # PHI Detection
    if result["phi_detection"]["phi_detected"]:
        print("\n--- PHI HANDLING DETECTED ---")
        print(f"  PHI Types: {', '.join(result['phi_detection']['phi_types'])}")
        print(f"  Files: {len(result['phi_detection']['files_with_phi'])}")

    # Vulnerabilities
    if result["vulnerabilities"]:
        print("\n--- SECURITY VULNERABILITIES ---")
        for vuln in result["vulnerabilities"][:10]:
            print(f"  - {vuln['vulnerability']}: {vuln['file']}")

    # Recommendations
    if result["recommendations"]:
        print("\n--- RECOMMENDATIONS ---")
        for i, rec in enumerate(result["recommendations"], 1):
            print(f"  {i}. {rec}")

    print("\n" + "=" * 70)
    print(f"Assessment Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 70)
