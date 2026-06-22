# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from growth_model_simulator_base import *  # noqa: F403,E402
# fmt: off
from growth_model_simulator_p1 import EXPANSION_RATE, GROSS_MARGIN, GROWTH_MODELS, MONTHLY_CHURN_RATE, ModelProjection, SIMULATION_MONTHS, STARTING_MRR  # noqa: E402,E501
from growth_model_simulator_p2 import fmt_currency, fmt_mrr, print_channel_overview, print_header, print_model_detail, simulate_model  # noqa: E402,E501
# fmt: on


def print_comparison_table(projections: List[ModelProjection]) -> None:
    print_header(f"Growth Model Comparison — Month {SIMULATION_MONTHS} Outcomes")
    header = (
        f"  {'Model':<20} {'MRR (final)':>12} {'ARR (final)':>12} "
        f"{'Growth':>7} {'LTV:CAC':>8} {'Break-even':>11}"
    )
    print(header)
    print("  " + "-" * 74)
    for proj in sorted(projections, key=lambda p: p.snapshots[-1].mrr, reverse=True):
        final = proj.snapshots[-1]
        growth_x = final.mrr / STARTING_MRR
        arr_final = final.mrr * 12
        be = f"Mo {proj.break_even_month}" if proj.break_even_month else f">{SIMULATION_MONTHS}mo"
        print(
            f"  {proj.model.name:<20} {fmt_mrr(final.mrr):>12} "
            f"{fmt_currency(arr_final):>12} {growth_x:>6.1f}x "
            f"{proj.model.avg_ltv_cac:>7.1f}x {be:>11}"
        )
def print_channel_mix_impact(projections: List[ModelProjection]) -> None:
    print_header("Channel Mix Impact Analysis")
    print("  How shifting channel mix changes growth trajectory:\n")
    baseline = next((p for p in projections if p.model.name == "Current Mix"), None)
    if not baseline:
        return
    baseline_final_mrr = baseline.snapshots[-1].mrr

    for proj in projections:
        if proj.model.name == "Current Mix":
            continue
        final_mrr = proj.snapshots[-1].mrr
        delta = final_mrr - baseline_final_mrr
        delta_pct = (delta / baseline_final_mrr) * 100
        arrow = "↑" if delta > 0 else "↓"
        m6_mrr = proj.snapshots[5].mrr if len(proj.snapshots) >= 6 else 0
        m6_baseline = baseline.snapshots[5].mrr if len(baseline.snapshots) >= 6 else 0
        m6_delta = m6_mrr - m6_baseline
        m6_pct = (m6_delta / m6_baseline) * 100 if m6_baseline else 0
        m6_arrow = "↑" if m6_delta > 0 else "↓"

        print(f"  {proj.model.name}:")
        print(f"    Month 6:  {m6_arrow} {abs(m6_pct):.1f}%  vs. current  ({fmt_mrr(m6_delta)} {'more' if m6_delta > 0 else 'less'} MRR)")
        print(f"    Month {SIMULATION_MONTHS}: {arrow} {abs(delta_pct):.1f}%  vs. current  ({fmt_mrr(delta)} {'more' if delta > 0 else 'less'} MRR)")
        if proj.model.months_to_steady_state > 4:
            print(f"    ⚠ Model takes {proj.model.months_to_steady_state} months to reach steady state — short-term dip expected.")
        print()
def print_decision_guide(projections: List[ModelProjection]) -> None:
    print_header("Decision Guide")
    print("  Choose your growth model based on your constraints:\n")
    guides = [
        ("ACV < $5K and fast time-to-value",         "PLG-First"),
        ("ACV > $25K and complex buying process",     "Sales-Led Scale"),
        ("Strong practitioner community exists",      "Community-Led"),
        ("Both SMB self-serve and enterprise buyers", "Hybrid PLS"),
        ("Uncertain — keep optionality",              "Current Mix"),
    ]
    for condition, model_name in guides:
        proj = next((p for p in projections if p.model.name == model_name), None)
        if proj:
            final_mrr = proj.snapshots[-1].mrr
            print(f"  If: {condition}")
            print(f"  → Use {model_name} → {fmt_mrr(final_mrr)} MRR at month {SIMULATION_MONTHS}")
            print()

    print("  Key question before switching models:")
    print("    'Do we have 12-18 months of runway to prove the new model")
    print("     while the current model continues in parallel?'")
    print("    If no → optimize current model. Don't switch.")
def main() -> None:
    print_channel_overview()

    projections = [simulate_model(model, SIMULATION_MONTHS) for model in GROWTH_MODELS]

    for proj in projections:
        print_model_detail(proj)

    print_comparison_table(projections)
    print_channel_mix_impact(projections)
    print_decision_guide(projections)

    print("\n" + "=" * 78)
    print("  Notes:")
    print(f"    Starting MRR:   {fmt_mrr(STARTING_MRR)}")
    print(f"    Simulation:     {SIMULATION_MONTHS} months")
    print(f"    Churn:          {MONTHLY_CHURN_RATE:.1%}/mo ({MONTHLY_CHURN_RATE*12:.0%} annualized)")
    print(f"    Expansion:      {EXPANSION_RATE:.1%}/mo of existing MRR")
    print(f"    Gross margin:   {GROSS_MARGIN:.0%}")
    print("    Acceleration rates are estimates — validate against your actuals.")
    print("=" * 78 + "\n")
