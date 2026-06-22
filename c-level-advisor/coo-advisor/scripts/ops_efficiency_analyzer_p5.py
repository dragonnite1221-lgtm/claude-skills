# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from ops_efficiency_analyzer_base import *  # noqa: F403,E402
# fmt: off
from ops_efficiency_analyzer_p1 import MetricsData  # noqa: E402,E501
# fmt: on


def generate_improvement_plan(
    process_scores: list[dict],
    bottleneck_analysis: dict,
    team_analysis: dict,
    metrics: MetricsData,
) -> list[dict]:
    """
    Generate a prioritized improvement plan combining all analysis outputs.
    Priority = Impact × Urgency / Effort
    """
    items = []

    # Priority 1: Process bottlenecks (Theory of Constraints — fix the constraint first)
    for b in bottleneck_analysis.get("bottlenecks", [])[:3]:
        items.append({
            "priority": 1,
            "category": "Bottleneck",
            "item": f"Resolve bottleneck in '{b['process']}' at step '{b['bottleneck_step']}'",
            "detail": b["toc_recommendation"],
            "impact": "HIGH — constraint limits entire system throughput",
            "effort": "MEDIUM",
            "owner_suggestion": "COO + process owner",
            "timebox": "2-4 weeks",
            "success_metric": f"Throughput at {b['bottleneck_step']} increases by 25%+",
        })

    # Priority 2: Critical process maturity gaps
    critical_processes = [
        p for p in process_scores if p["maturity_score"] < 2.0
    ]
    for proc in sorted(critical_processes, key=lambda x: x["maturity_score"]):
        for rec in proc["recommendations"][:2]:  # Top 2 recs per critical process
            items.append({
                "priority": 2,
                "category": "Process Maturity",
                "item": f"Fix {rec['dimension']} in '{proc['name']}' (score: {rec['current_score']}/5)",
                "detail": rec["action"],
                "impact": "HIGH — ad-hoc processes create inconsistency and risk",
                "effort": "LOW-MEDIUM",
                "owner_suggestion": "Process owner",
                "timebox": "1-2 weeks",
                "success_metric": f"Dimension score improves to 3/5",
            })

    # Priority 3: Team structural issues
    for issue in team_analysis.get("structural_issues", []):
        items.append({
            "priority": 3,
            "category": "Org Structure",
            "item": issue["type"],
            "detail": issue["detail"],
            "impact": "MEDIUM — structural issues compound over time",
            "effort": "HIGH",
            "owner_suggestion": "COO + People",
            "timebox": "1-2 quarters",
            "success_metric": "Management layer count normalized",
        })

    for span_issue in team_analysis.get("span_of_control_issues", []):
        severity = "HIGH" if span_issue["issue"] == "Over-span" else "MEDIUM"
        items.append({
            "priority": 3,
            "category": "Span of Control",
            "item": f"{span_issue['issue']}: {span_issue['manager']} ({span_issue['dept']})",
            "detail": span_issue["recommendation"],
            "impact": severity,
            "effort": "MEDIUM",
            "owner_suggestion": f"VP {span_issue['dept']}",
            "timebox": "1 quarter",
            "success_metric": "Span within 5-8 for ICs, 3-5 for managers",
        })

    # Priority 4: Maturity improvements for non-critical processes
    medium_processes = [
        p for p in process_scores if 2.0 <= p["maturity_score"] < 3.5
    ]
    for proc in sorted(medium_processes, key=lambda x: x["maturity_score"])[:3]:
        if proc["recommendations"]:
            top_rec = proc["recommendations"][0]
            items.append({
                "priority": 4,
                "category": "Process Improvement",
                "item": f"Improve {top_rec['dimension']} in '{proc['name']}'",
                "detail": top_rec["action"],
                "impact": "MEDIUM",
                "effort": "LOW",
                "owner_suggestion": "Process owner",
                "timebox": "2-4 weeks",
                "success_metric": f"Dimension score reaches 3/5",
            })

    # Priority 5: Metrics-driven flags
    burn_multiple = metrics.get("burn_multiple")
    if burn_multiple and burn_multiple > 2.0:
        items.append({
            "priority": 2,
            "category": "Financial Efficiency",
            "item": f"Burn multiple of {burn_multiple:.1f}x is above healthy range",
            "detail": "Burn multiple >1.5x indicates spending exceeds efficient growth. Review headcount-to-revenue ratio by department.",
            "impact": "HIGH",
            "effort": "MEDIUM",
            "owner_suggestion": "COO + CFO",
            "timebox": "30 days to diagnose, 60-90 days to act",
            "success_metric": "Burn multiple <1.5x within 2 quarters",
        })

    nrr = metrics.get("net_revenue_retention_pct")
    if nrr and nrr < 100:
        items.append({
            "priority": 1,
            "category": "Revenue Health",
            "item": f"NRR of {nrr}% — losing more from churn/contraction than gaining from expansion",
            "detail": "NRR <100% means the customer base shrinks without new sales. Investigate churn root causes immediately.",
            "impact": "CRITICAL",
            "effort": "HIGH",
            "owner_suggestion": "COO + VP CS",
            "timebox": "Immediate — 30 days to root cause, 90 days to fix",
            "success_metric": "NRR >100% within 2 quarters",
        })

    # Sort by priority then impact
    priority_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    items.sort(key=lambda x: (x["priority"], priority_order.get(x["impact"].split(" — ")[0], 9)))

    return items
