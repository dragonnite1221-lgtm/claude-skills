# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from review_report_generator_base import *  # noqa: F403,E402
# fmt: off
from review_report_generator_p1 import calculate_review_score, determine_verdict, run_pr_analyzer, run_quality_checker  # noqa: E402,E501
from review_report_generator_p2 import generate_action_items, generate_findings_list  # noqa: E402,E501
# fmt: on


def format_text_report(report: Dict) -> str:
    """Generate plain text report."""
    lines = []

    lines.append("=" * 60)
    lines.append("CODE REVIEW REPORT")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"Generated: {report['metadata']['generated_at']}")
    lines.append(f"Repository: {report['metadata']['repository']}")
    lines.append("")

    summary = report["summary"]
    verdict = summary["verdict"].upper().replace("_", " ")
    lines.append(f"VERDICT: {verdict}")
    lines.append(f"SCORE: {summary['score']}/100")
    lines.append(f"RATIONALE: {summary['rationale']}")
    lines.append("")

    lines.append("--- ISSUE SUMMARY ---")
    for severity in ["critical", "high", "medium", "low"]:
        count = summary["issue_counts"].get(severity, 0)
        lines.append(f"  {severity.capitalize()}: {count}")
    lines.append("")

    if report.get("action_items"):
        lines.append("--- ACTION ITEMS ---")
        for i, item in enumerate(report["action_items"][:10], 1):
            lines.append(f"  {i}. [{item['priority']}] {item['action']}")
        lines.append("")

    critical = [f for f in report.get("findings", []) if f["severity"] == "critical"]
    if critical:
        lines.append("--- CRITICAL ISSUES ---")
        for f in critical:
            lines.append(f"  [{f.get('file', 'unknown')}] {f['message']}")
        lines.append("")

    lines.append("=" * 60)

    return "\n".join(lines)
def generate_report(
    repo_path: Path,
    pr_analysis: Optional[Dict] = None,
    quality_analysis: Optional[Dict] = None
) -> Dict:
    """Generate comprehensive review report."""
    # Run analyses if not provided
    if pr_analysis is None:
        pr_analysis = run_pr_analyzer(repo_path)

    if quality_analysis is None:
        quality_analysis = run_quality_checker(repo_path)

    # Generate findings
    findings = generate_findings_list(pr_analysis, quality_analysis)

    # Count issues by severity
    issue_counts = {
        "critical": len([f for f in findings if f["severity"] == "critical"]),
        "high": len([f for f in findings if f["severity"] == "high"]),
        "medium": len([f for f in findings if f["severity"] == "medium"]),
        "low": len([f for f in findings if f["severity"] == "low"])
    }

    # Calculate score and verdict
    score = calculate_review_score(pr_analysis, quality_analysis)
    verdict, rationale = determine_verdict(
        score,
        issue_counts["critical"],
        issue_counts["high"]
    )

    # Generate action items
    action_items = generate_action_items(findings)

    # Build report
    report = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "repository": str(repo_path),
            "version": "1.0.0"
        },
        "summary": {
            "score": score,
            "verdict": verdict,
            "rationale": rationale,
            "issue_counts": issue_counts
        },
        "findings": findings,
        "action_items": action_items
    }

    # Add PR summary if available
    if pr_analysis.get("status") == "analyzed":
        report["pr_summary"] = pr_analysis.get("summary", {})
        report["review_order"] = pr_analysis.get("review_order", [])

    # Add quality summary if available
    if quality_analysis.get("status") == "analyzed":
        report["quality_summary"] = quality_analysis.get("summary", {})

    return report
