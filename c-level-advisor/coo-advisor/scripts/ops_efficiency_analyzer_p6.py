# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from ops_efficiency_analyzer_base import *  # noqa: F403,E402
# fmt: off
from ops_efficiency_analyzer_p1 import MATURITY_LEVELS, MetricsData  # noqa: E402,E501
# fmt: on


def format_report(
    process_scores: list[dict],
    bottleneck_analysis: dict,
    team_analysis: dict,
    improvement_plan: list[dict],
    metrics: MetricsData,
) -> str:
    """Format the full analysis report as plain text."""
    lines = []
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines.append("=" * 70)
    lines.append("OPERATIONAL EFFICIENCY ANALYSIS REPORT")
    lines.append(f"Generated: {now}")
    lines.append("=" * 70)

    # --- Executive Summary ---
    lines.append("\n📊 EXECUTIVE SUMMARY")
    lines.append("-" * 40)

    avg_maturity = (
        sum(p["maturity_score"] for p in process_scores) / len(process_scores)
        if process_scores else 0
    )
    critical_count = sum(1 for p in process_scores if p["maturity_score"] < 2.0)
    bottleneck_count = len(bottleneck_analysis.get("bottlenecks", []))
    plan_items = len(improvement_plan)

    lines.append(f"Average Process Maturity:  {avg_maturity:.1f}/5.0  ({MATURITY_LEVELS.get(round(avg_maturity), 'Unknown')})")
    lines.append(f"Critical Process Gaps:     {critical_count}")
    lines.append(f"Active Bottlenecks:        {bottleneck_count}")
    lines.append(f"Improvement Plan Items:    {plan_items}")

    if metrics:
        lines.append("\nKey Business Metrics:")
        if metrics.get("burn_multiple"):
            flag = " ⚠️" if metrics["burn_multiple"] > 2.0 else ""
            lines.append(f"  Burn Multiple:           {metrics['burn_multiple']:.1f}x{flag}")
        if metrics.get("net_revenue_retention_pct"):
            flag = " ⚠️" if metrics["net_revenue_retention_pct"] < 100 else ""
            lines.append(f"  NRR:                     {metrics['net_revenue_retention_pct']}%{flag}")
        if metrics.get("cac_payback_months"):
            flag = " ⚠️" if metrics["cac_payback_months"] > 18 else ""
            lines.append(f"  CAC Payback:             {metrics['cac_payback_months']} months{flag}")

    # --- Process Maturity Scores ---
    lines.append("\n\n📋 PROCESS MATURITY SCORES")
    lines.append("-" * 40)
    lines.append(f"{'Process':<35} {'Score':>6}  {'Level':<12} {'Status'}")
    lines.append(f"{'─'*35} {'─'*6}  {'─'*12} {'─'*20}")

    for p in sorted(process_scores, key=lambda x: x["maturity_score"]):
        score = p["maturity_score"]
        label = p["maturity_label"]
        status = "🔴 Critical" if score < 2 else ("🟡 Needs work" if score < 3.5 else "🟢 Healthy")
        lines.append(f"{p['name']:<35} {score:>6.1f}  {label:<12} {status}")

    # Dimension heatmap
    lines.append("\n\nDimension Breakdown (scores 0-5):")
    lines.append(f"{'Process':<30} {'Doc':>4} {'Own':>4} {'Met':>4} {'Aut':>4} {'Con':>4} {'Fbk':>4}")
    lines.append(f"{'─'*30} {'─'*4} {'─'*4} {'─'*4} {'─'*4} {'─'*4} {'─'*4}")
    for p in sorted(process_scores, key=lambda x: x["maturity_score"]):
        d = p["dimension_scores"]
        lines.append(
            f"{p['name']:<30} {d.get('documentation',0):>4} {d.get('ownership',0):>4} "
            f"{d.get('metrics',0):>4} {d.get('automation',0):>4} "
            f"{d.get('consistency',0):>4} {d.get('feedback_loop',0):>4}"
        )

    # --- Bottleneck Analysis ---
    lines.append("\n\n🔍 BOTTLENECK ANALYSIS (Theory of Constraints)")
    lines.append("-" * 40)

    bottlenecks = bottleneck_analysis.get("bottlenecks", [])
    if not bottlenecks:
        lines.append("No process steps defined for bottleneck analysis.")
    else:
        for i, b in enumerate(bottlenecks, 1):
            lines.append(f"\n{i}. {b['process']}")
            lines.append(f"   Bottleneck step:    {b['bottleneck_step']}")
            lines.append(f"   Throughput:         {b['bottleneck_throughput']}/day")
            lines.append(f"   Queue depth:        {b['bottleneck_queue']} units")
            lines.append(f"   Flow efficiency:    {b['flow_efficiency_pct']}%")
            lines.append(f"   Recommendation:     {b['toc_recommendation']}")

            lines.append(f"\n   Step-by-step throughput:")
            for step in b["steps"]:
                marker = " ← BOTTLENECK" if step["is_bottleneck"] else ""
                lines.append(
                    f"     {step['name']:<30} {step['throughput_per_day']:>4}/day  "
                    f"Queue: {step['queue_depth']:>4}  Util: {step['utilization_pct']:>5.1f}%{marker}"
                )

    # --- Team Structure ---
    lines.append("\n\n👥 TEAM STRUCTURE ANALYSIS")
    lines.append("-" * 40)
    lines.append(f"Total headcount:    {team_analysis['total_headcount']}")
    lines.append(f"Management layers:  {team_analysis['management_layers']} (expected: {team_analysis['expected_layers']})")

    span_issues = team_analysis.get("span_of_control_issues", [])
    if span_issues:
        lines.append(f"\n⚠️  Span of Control Issues ({len(span_issues)}):")
        for issue in span_issues:
            lines.append(f"   {issue['issue']}: {issue['manager']} ({issue['dept']}) — {issue['reports']} reports")
            lines.append(f"   → {issue['recommendation']}")

    dept_eff = team_analysis.get("department_efficiency", [])
    if dept_eff:
        lines.append(f"\nDepartment Revenue Efficiency:")
        lines.append(f"{'Department':<20} {'HC':>4} {'Rev/Head':>10} {'Benchmark':>10} {'vs Bench':>9} {'Status'}")
        lines.append(f"{'─'*20} {'─'*4} {'─'*10} {'─'*10} {'─'*9} {'─'*20}")
        for d in dept_eff:
            rev = f"${d['revenue_per_employee']:,}" if d['revenue_per_employee'] else "N/A"
            bench = f"${d['benchmark']:,}" if d['benchmark'] else "N/A"
            vs_bench = f"{d['efficiency_vs_benchmark_pct']}%" if d['efficiency_vs_benchmark_pct'] != "N/A" else "N/A"
            lines.append(
                f"{d['department']:<20} {d['headcount']:>4} {rev:>10} {bench:>10} {vs_bench:>9} {d['status']}"
            )

    # --- Improvement Plan ---
    lines.append("\n\n🎯 PRIORITIZED IMPROVEMENT PLAN")
    lines.append("-" * 40)
    lines.append("Items ranked by priority (1=highest). Fix Priority 1 before starting Priority 2.\n")

    current_priority = None
    for i, item in enumerate(improvement_plan, 1):
        if item["priority"] != current_priority:
            current_priority = item["priority"]
            lines.append(f"\nPRIORITY {current_priority}")
            lines.append("─" * 30)

        lines.append(f"\n{i}. [{item['category']}] {item['item']}")
        lines.append(f"   Detail:   {item['detail']}")
        lines.append(f"   Impact:   {item['impact']}")
        lines.append(f"   Effort:   {item['effort']}")
        lines.append(f"   Owner:    {item['owner_suggestion']}")
        lines.append(f"   Timebox:  {item['timebox']}")
        lines.append(f"   Success:  {item['success_metric']}")

    lines.append("\n" + "=" * 70)
    lines.append("END OF REPORT")
    lines.append("=" * 70)

    return "\n".join(lines)
