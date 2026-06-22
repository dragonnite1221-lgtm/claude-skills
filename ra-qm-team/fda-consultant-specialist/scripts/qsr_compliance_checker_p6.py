# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from qsr_compliance_checker_base import *  # noqa: F403,E402
# fmt: off
from qsr_compliance_checker_p3 import QSR_REQUIREMENTS  # noqa: E402,E501
from qsr_compliance_checker_p4 import assess_section  # noqa: E402,E501
from qsr_compliance_checker_p5 import calculate_overall_compliance, generate_gap_report, print_text_report  # noqa: E402,E501
# fmt: on


def main():
    parser = argparse.ArgumentParser(
        description="QSR Compliance Checker - Assess 21 CFR 820 compliance"
    )
    parser.add_argument(
        "project_dir",
        nargs="?",
        default=".",
        help="Project directory to analyze (default: current directory)"
    )
    parser.add_argument(
        "--section",
        help="Analyze specific QSR section only (e.g., 820.30)"
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

    # Filter sections if specific one requested
    sections_to_assess = QSR_REQUIREMENTS
    if args.section:
        if args.section in QSR_REQUIREMENTS:
            sections_to_assess = {args.section: QSR_REQUIREMENTS[args.section]}
        else:
            print(f"Error: Unknown section: {args.section}", file=sys.stderr)
            print(f"Available sections: {', '.join(QSR_REQUIREMENTS.keys())}")
            sys.exit(1)

    # Perform assessment
    assessment_results = []
    for section_id, section_data in sections_to_assess.items():
        section_result = assess_section(project_dir, section_id, section_data)
        assessment_results.append(section_result)

    # Generate reports
    overall_compliance = calculate_overall_compliance(assessment_results)
    gap_report = generate_gap_report(assessment_results)

    result = {
        "project_dir": str(project_dir),
        "assessment_date": datetime.now().isoformat(),
        "overall_compliance": overall_compliance,
        "assessment": assessment_results if args.detailed else [
            {
                "section": s["section"],
                "title": s["title"],
                "compliance_score": s["compliance_score"],
                "status": "compliant" if s["compliance_score"] >= 70 else "gap"
            }
            for s in assessment_results
        ],
        "gap_report": gap_report
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_text_report(result)
