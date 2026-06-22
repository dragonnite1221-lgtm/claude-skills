# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from churn_risk_analyzer_base import *  # noqa: F403,E402
# fmt: off
from churn_risk_analyzer_p1 import INTERVENTION_PLAYBOOKS, RISK_SIGNAL_WEIGHTS, WARNING_SEVERITY, clamp, days_until, get_risk_tier, renewal_urgency_multiplier, score_usage_decline  # noqa: E402,E501
from churn_risk_analyzer_p2 import score_commercial_factors, score_engagement_drop, score_relationship_signals, score_support_issues  # noqa: E402,E501
# fmt: on


def analyse_churn_risk(customer: Dict[str, Any]) -> Dict[str, Any]:
    """Analyse churn risk for a single customer."""
    usage_score, usage_warnings = score_usage_decline(customer.get("usage_decline", {}))
    engagement_score, engagement_warnings = score_engagement_drop(customer.get("engagement_drop", {}))
    support_score, support_warnings = score_support_issues(customer.get("support_issues", {}))
    relationship_score, relationship_warnings = score_relationship_signals(customer.get("relationship_signals", {}))
    commercial_score, commercial_warnings = score_commercial_factors(customer.get("commercial_factors", {}))

    # Weighted raw score
    raw_score = (
        usage_score * RISK_SIGNAL_WEIGHTS["usage_decline"]
        + engagement_score * RISK_SIGNAL_WEIGHTS["engagement_drop"]
        + support_score * RISK_SIGNAL_WEIGHTS["support_issues"]
        + relationship_score * RISK_SIGNAL_WEIGHTS["relationship_signals"]
        + commercial_score * RISK_SIGNAL_WEIGHTS["commercial_factors"]
    )

    # Apply renewal urgency multiplier
    remaining = days_until(customer.get("contract_end_date"))
    multiplier = renewal_urgency_multiplier(remaining)
    adjusted_score = clamp(round(raw_score * multiplier, 1))

    tier = get_risk_tier(adjusted_score)

    # Collect and sort warnings by severity
    all_warnings = usage_warnings + engagement_warnings + support_warnings + relationship_warnings + commercial_warnings
    all_warnings.sort(key=lambda w: WARNING_SEVERITY.get(w["severity"], 0), reverse=True)

    playbook = INTERVENTION_PLAYBOOKS.get(tier["name"], [])

    return {
        "customer_id": customer.get("customer_id", "unknown"),
        "name": customer.get("name", "Unknown"),
        "segment": customer.get("segment", "unknown"),
        "arr": customer.get("arr", 0),
        "risk_score": adjusted_score,
        "raw_score": round(raw_score, 1),
        "risk_tier": tier["name"],
        "risk_label": tier["label"],
        "urgency_multiplier": multiplier,
        "days_to_renewal": remaining,
        "signal_scores": {
            "usage_decline": {"score": usage_score, "weight": "30%"},
            "engagement_drop": {"score": engagement_score, "weight": "25%"},
            "support_issues": {"score": support_score, "weight": "20%"},
            "relationship_signals": {"score": relationship_score, "weight": "15%"},
            "commercial_factors": {"score": commercial_score, "weight": "10%"},
        },
        "warning_signals": all_warnings,
        "recommended_actions": playbook,
    }
def format_text(results: List[Dict[str, Any]]) -> str:
    """Format results as human-readable text."""
    lines: List[str] = []
    lines.append("=" * 72)
    lines.append("CHURN RISK ANALYSIS REPORT")
    lines.append("=" * 72)
    lines.append("")

    total = len(results)
    critical_count = sum(1 for r in results if r["risk_tier"] == "critical")
    high_count = sum(1 for r in results if r["risk_tier"] == "high")
    medium_count = sum(1 for r in results if r["risk_tier"] == "medium")
    low_count = sum(1 for r in results if r["risk_tier"] == "low")
    total_arr_at_risk = sum(r["arr"] for r in results if r["risk_tier"] in ("critical", "high"))

    lines.append(f"Portfolio Summary: {total} customers analysed")
    lines.append(f"  Critical Risk: {critical_count}")
    lines.append(f"  High Risk:     {high_count}")
    lines.append(f"  Medium Risk:   {medium_count}")
    lines.append(f"  Low Risk:      {low_count}")
    lines.append(f"  ARR at Risk (Critical + High): ${total_arr_at_risk:,.0f}")
    lines.append("")

    # Sort by risk score descending
    sorted_results = sorted(results, key=lambda r: r["risk_score"], reverse=True)

    for r in sorted_results:
        lines.append("-" * 72)
        lines.append(f"Customer: {r['name']} ({r['customer_id']})")
        lines.append(f"Segment:  {r['segment'].title()}  |  ARR: ${r['arr']:,.0f}")
        renewal_str = f"{r['days_to_renewal']} days" if r["days_to_renewal"] is not None else "N/A"
        lines.append(f"Risk Score: {r['risk_score']}/100  [{r['risk_label']}]  |  Renewal: {renewal_str}")
        if r["urgency_multiplier"] > 1.0:
            lines.append(f"  ** Urgency multiplier applied: {r['urgency_multiplier']}x (renewal approaching)")
        lines.append("")

        lines.append("  Signal Scores:")
        for signal_name, signal_data in r["signal_scores"].items():
            display_name = signal_name.replace("_", " ").title()
            lines.append(f"    {display_name:25s} {signal_data['score']:6.1f}/100  ({signal_data['weight']})")

        if r["warning_signals"]:
            lines.append("")
            lines.append("  Warning Signals:")
            for w in r["warning_signals"]:
                severity_tag = w["severity"].upper()
                lines.append(f"    [{severity_tag}] {w['signal']}")

        if r["recommended_actions"]:
            lines.append("")
            lines.append("  Recommended Actions:")
            for i, action in enumerate(r["recommended_actions"], 1):
                lines.append(f"    {i}. {action}")

        lines.append("")

    lines.append("=" * 72)
    return "\n".join(lines)
def format_json(results: List[Dict[str, Any]]) -> str:
    """Format results as JSON."""
    total = len(results)
    output = {
        "report": "churn_risk_analysis",
        "summary": {
            "total_customers": total,
            "critical_count": sum(1 for r in results if r["risk_tier"] == "critical"),
            "high_count": sum(1 for r in results if r["risk_tier"] == "high"),
            "medium_count": sum(1 for r in results if r["risk_tier"] == "medium"),
            "low_count": sum(1 for r in results if r["risk_tier"] == "low"),
            "total_arr_at_risk": sum(r["arr"] for r in results if r["risk_tier"] in ("critical", "high")),
        },
        "customers": sorted(results, key=lambda r: r["risk_score"], reverse=True),
    }
    return json.dumps(output, indent=2)
