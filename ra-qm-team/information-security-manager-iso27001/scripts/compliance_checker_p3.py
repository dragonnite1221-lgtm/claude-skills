# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from compliance_checker_base import *  # noqa: F403,E402
# fmt: off
from compliance_checker_p2 import generate_gap_analysis  # noqa: E402,E501
# fmt: on


def format_output(
    results: Dict[str, Any],
    gap_analysis: bool,
    output_format: str
) -> str:
    """Format compliance results for output."""
    if output_format == "json":
        if gap_analysis:
            results["gap_analysis"] = generate_gap_analysis(results)
        return json.dumps(results, indent=2)

    # Markdown format
    lines = [
        f"# {results['standard'].upper()} Compliance Report",
        f"",
        f"**Generated:** {results['timestamp']}",
        f"",
        f"## Summary",
        f"",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Total Controls | {results['summary']['total_controls']} |",
        f"| Implemented | {results['summary']['implemented']} |",
        f"| Partial | {results['summary']['partial']} |",
        f"| Not Implemented | {results['summary']['not_implemented']} |",
        f"| **Compliance** | **{results['summary']['compliance_percentage']}%** |",
        f"",
    ]

    # Domain breakdown
    lines.extend([
        f"## Compliance by Domain",
        f"",
        f"| Domain | Implemented | Partial | Not Impl | Score |",
        f"|--------|-------------|---------|----------|-------|",
    ])

    for domain_key, domain_data in results["domains"].items():
        total = len(domain_data["controls"])
        score = round(
            ((domain_data["implemented"] + domain_data["partial"] * 0.5) / total) * 100
        ) if total > 0 else 0
        lines.append(
            f"| {domain_data['name']} | {domain_data['implemented']} | "
            f"{domain_data['partial']} | {domain_data['not_implemented']} | {score}% |"
        )

    # Findings
    if results["findings"]:
        lines.extend([
            f"",
            f"## Priority Findings",
            f"",
            f"| Control | Name | Priority | Status |",
            f"|---------|------|----------|--------|",
        ])
        for finding in results["findings"][:15]:  # Top 15
            lines.append(
                f"| {finding['control_id']} | {finding['control_name']} | "
                f"{finding['priority'].capitalize()} | {finding['status'].replace('_', ' ').capitalize()} |"
            )

    # Gap analysis
    if gap_analysis:
        gaps = generate_gap_analysis(results)
        lines.extend([
            f"",
            f"## Gap Analysis & Remediation",
            f"",
        ])
        for gap in gaps[:10]:  # Top 10 gaps
            lines.extend([
                f"### {gap['control_id']}: {gap['control_name']}",
                f"",
                f"- **Priority:** {gap['priority'].capitalize()}",
                f"- **Current Status:** {gap['current_status'].replace('_', ' ').capitalize()}",
                f"- **Remediation:** {gap['remediation']}",
                f"- **Timeline:** {gap['timeline']}",
                f"",
            ])

    return "\n".join(lines)
