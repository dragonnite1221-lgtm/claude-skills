# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from gap_analyzer_base import *  # noqa: F403,E402
# fmt: off
from gap_analyzer_p1 import load_controls  # noqa: E402,E501
from gap_analyzer_p2 import analyze_coverage, detect_categories  # noqa: E402,E501
from gap_analyzer_p3 import analyze_type2_gaps, build_report  # noqa: E402,E501
# fmt: on


def format_text_report(report: Dict[str, Any]) -> str:
    """Format the gap analysis report as human-readable text."""
    lines = [
        "=" * 65,
        "SOC 2 Gap Analysis Report",
        "=" * 65,
        "",
    ]

    meta = report["report_metadata"]
    lines.append(f"Audit Type:    {meta['audit_type'].upper()}")
    lines.append(f"Report Date:   {meta['report_date']}")
    lines.append(f"Categories:    {', '.join(meta['categories_assessed'])}")
    lines.append(f"Controls:      {meta['total_controls_assessed']}")
    lines.append("")

    # Coverage summary
    cov = report["coverage_summary"]
    lines.append("--- Coverage Summary ---")
    lines.append(f"  Total TSC Criteria:    {cov['total_criteria']}")
    lines.append(f"  Fully Covered:         {cov['covered']}")
    lines.append(f"  Partially Covered:     {cov['partially_covered']}")
    lines.append(f"  Missing:               {cov['missing']}")
    lines.append(f"  Coverage:              {cov['coverage_percentage']}%")
    lines.append(f"  Critical Gaps:         {cov['critical_gaps']}")
    lines.append(f"  Readiness:             {cov['readiness_assessment']}")
    lines.append("")

    # Gaps
    gaps = report.get("gaps", [])
    if gaps:
        lines.append(f"--- Missing Controls ({len(gaps)}) ---")
        for g in gaps:
            sev = g["severity"].upper()
            lines.append(
                f"  [{sev}] {g['tsc_criteria']}: {g['description']}"
            )
            lines.append(f"         Remediation: {g['remediation']}")
        lines.append("")

    # Partial
    partial = report.get("partial_implementations", [])
    if partial:
        lines.append(f"--- Partial Implementations ({len(partial)}) ---")
        for p in partial:
            ctrls = ", ".join(p.get("controls", []))
            lines.append(
                f"  [{p['severity'].upper()}] {p['tsc_criteria']}: {p['description']}"
            )
            lines.append(f"         Controls: {ctrls}")
            lines.append(f"         Remediation: {p['remediation']}")
        lines.append("")

    # Type II operating gaps
    if "type2_operating_gaps" in report:
        t2 = report["type2_operating_gaps"]
        lines.append(
            f"--- Type II Operating Gaps ({t2['controls_with_issues']} controls, {t2['total_issues']} issues) ---"
        )
        for detail in t2["details"]:
            lines.append(f"  [{detail['control_id']}] {detail['description']}")
            for issue in detail["issues"]:
                lines.append(
                    f"    - [{issue['severity'].upper()}] {issue['check']}: {issue['detail']}"
                )
        lines.append("")

    return "\n".join(lines)
def main():
    parser = argparse.ArgumentParser(
        description="SOC 2 Gap Analyzer — identifies gaps between current controls and SOC 2 requirements."
    )
    parser.add_argument(
        "--controls",
        type=str,
        required=True,
        help="Path to JSON file with current controls (from control_matrix_builder.py or custom)",
    )
    parser.add_argument(
        "--type",
        type=str,
        choices=["type1", "type2"],
        default="type1",
        help="Audit type: type1 (design only) or type2 (design + operating effectiveness)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format",
    )

    args = parser.parse_args()

    controls = load_controls(args.controls)
    categories = detect_categories(controls)
    gaps, partial, covered = analyze_coverage(controls, categories)

    type2_gaps = []
    if args.type == "type2":
        type2_gaps = analyze_type2_gaps(controls)

    report = build_report(
        controls, args.type, categories, gaps, partial, covered, type2_gaps
    )

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(format_text_report(report))
