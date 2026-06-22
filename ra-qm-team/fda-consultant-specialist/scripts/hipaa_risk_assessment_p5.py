# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from hipaa_risk_assessment_base import *  # noqa: F403,E402
# fmt: off
from hipaa_risk_assessment_p1 import HIPAA_SAFEGUARDS  # noqa: E402,E501
from hipaa_risk_assessment_p2 import detect_phi_handling  # noqa: E402,E501
from hipaa_risk_assessment_p3 import assess_category, calculate_risk_level, detect_security_vulnerabilities  # noqa: E402,E501
from hipaa_risk_assessment_p4 import generate_recommendations, print_text_report  # noqa: E402,E501
# fmt: on


def main():
    parser = argparse.ArgumentParser(
        description="HIPAA Risk Assessment Tool for Medical Device Software"
    )
    parser.add_argument(
        "project_dir",
        nargs="?",
        default=".",
        help="Project directory to analyze (default: current directory)"
    )
    parser.add_argument(
        "--category",
        choices=["administrative", "physical", "technical"],
        help="Assess specific safeguard category only"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format"
    )
    parser.add_argument(
        "--detailed",
        action="store_true",
        help="Include detailed evidence in output"
    )

    args = parser.parse_args()
    project_dir = Path(args.project_dir).resolve()

    if not project_dir.exists():
        print(f"Error: Directory not found: {project_dir}", file=sys.stderr)
        sys.exit(1)

    # Filter categories if specific one requested
    categories_to_assess = HIPAA_SAFEGUARDS
    if args.category:
        categories_to_assess = {args.category: HIPAA_SAFEGUARDS[args.category]}

    # Perform assessment
    category_results = []
    total_weight = 0
    weighted_score = 0

    for cat_id, cat_data in categories_to_assess.items():
        cat_result = assess_category(project_dir, cat_id, cat_data)
        category_results.append(cat_result)

        # Calculate weighted average
        cat_weight = sum(c["weight"] for c in cat_data["controls"].values())
        total_weight += cat_weight
        weighted_score += (cat_result["score"] * cat_weight) / 100

    overall_score = round((weighted_score / total_weight) * 100, 1) if total_weight > 0 else 0

    # Additional scans
    phi_detection = detect_phi_handling(project_dir)
    vulnerabilities = detect_security_vulnerabilities(project_dir)

    # Risk assessment
    risk_assessment = calculate_risk_level(overall_score, vulnerabilities, phi_detection)

    result = {
        "project_dir": str(project_dir),
        "assessment_date": datetime.now().isoformat(),
        "overall_score": overall_score,
        "risk_assessment": risk_assessment,
        "categories": category_results if args.detailed else [
            {
                "category": c["category"],
                "title": c["title"],
                "score": c["score"],
                "compliant": c["compliant"],
                "partial": c["partial"],
                "gaps": c["gaps"]
            }
            for c in category_results
        ],
        "phi_detection": phi_detection,
        "vulnerabilities": vulnerabilities,
        "recommendations": []
    }

    result["recommendations"] = generate_recommendations(result)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_text_report(result)
