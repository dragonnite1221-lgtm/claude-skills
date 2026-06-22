# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from growth_model_simulator_base import *  # noqa: F403,E402
# fmt: off
from growth_model_simulator_p1 import CHANNELS, EXPANSION_RATE, GROSS_MARGIN, GrowthModel, MONTHLY_CHURN_RATE, ModelProjection, MonthSnapshot, SIMULATION_MONTHS, STARTING_MRR, _weighted_cac  # noqa: E402,E501
# fmt: on


def simulate_model(model: GrowthModel, months: int) -> ModelProjection:
    snapshots: List[MonthSnapshot] = []
    mrr = STARTING_MRR
    cumulative_cac = 0.0
    cumulative_revenue = 0.0
    break_even_month = None

    for m in range(1, months + 1):
        # Ramp up — new_mrr accelerates each month
        if m <= model.months_to_steady_state:
            # Ramp phase: linear ramp from 60% to 100% of base
            ramp_factor = 0.6 + 0.4 * (m / model.months_to_steady_state)
        else:
            # Steady state: compound acceleration
            months_past_ramp = m - model.months_to_steady_state
            ramp_factor = 1.0 + model.monthly_acceleration * months_past_ramp

        new_mrr = model.new_mrr_monthly_base * ramp_factor
        churned_mrr = mrr * MONTHLY_CHURN_RATE
        expansion_mrr = mrr * EXPANSION_RATE
        net_new_mrr = new_mrr - churned_mrr + expansion_mrr
        mrr = mrr + net_new_mrr

        # CAC spend approximation: new_mrr / (avg_deal_mrr) * blended_cac
        # Use weighted CAC from channel mix
        weighted_cac = _weighted_cac(model.channel_mix)
        avg_deal_mrr = 1_500  # Assumption: $1,500 average deal MRR
        deals_this_month = new_mrr / avg_deal_mrr
        cac_spend = deals_this_month * weighted_cac
        cumulative_cac += cac_spend
        cumulative_revenue += mrr * GROSS_MARGIN

        if break_even_month is None and cumulative_revenue >= cumulative_cac:
            break_even_month = m

        snapshots.append(MonthSnapshot(
            month=m,
            mrr=mrr,
            new_mrr=new_mrr,
            churned_mrr=churned_mrr,
            expansion_mrr=expansion_mrr,
            net_new_mrr=net_new_mrr,
            cumulative_cac_spend=cumulative_cac,
        ))

    return ModelProjection(
        model=model,
        snapshots=snapshots,
        break_even_month=break_even_month,
    )
def fmt_mrr(n: float) -> str:
    if n >= 1_000_000:
        return f"${n/1_000_000:.3f}M"
    return f"${n/1_000:.1f}K"
def fmt_currency(n: float) -> str:
    if n >= 1_000_000:
        return f"${n/1_000_000:.2f}M"
    if n >= 1_000:
        return f"${n/1_000:.1f}K"
    return f"${n:.0f}"
def print_header(title: str) -> None:
    width = 78
    print("\n" + "=" * width)
    print(f"  {title}")
    print("=" * width)
def print_channel_overview() -> None:
    print_header("Current Channel Mix")
    print(f"  Starting MRR: {fmt_mrr(STARTING_MRR)}  |  Monthly churn: {MONTHLY_CHURN_RATE:.1%}  |  Expansion: {EXPANSION_RATE:.1%}/mo")
    print()
    print(f"  {'Channel':<22} {'% MRR':>7} {'CAC':>8} {'Payback':>9} {'Growth/mo':>10}")
    print("  " + "-" * 60)
    for ch in sorted(CHANNELS, key=lambda c: c.pct_of_new_mrr, reverse=True):
        print(
            f"  {ch.name:<22} {ch.pct_of_new_mrr:>6.0%} "
            f"{fmt_currency(ch.cac):>8} {ch.payback_months:>7.0f}mo "
            f"{ch.monthly_growth_rate:>9.1%}"
        )
def print_model_detail(proj: ModelProjection) -> None:
    model = proj.model
    print_header(f"Model: {model.name}")
    print(f"  {model.description}")
    if model.notes:
        print()
        for note in model.notes:
            print(f"  • {note}")
    print()

    # Print monthly snapshot (every 3 months + final)
    milestones = set(range(3, SIMULATION_MONTHS + 1, 3)) | {SIMULATION_MONTHS}
    print(f"  {'Month':<7} {'MRR':>10} {'New MRR':>9} {'Churned':>9} {'Expand':>8} {'Net New':>9}")
    print("  " + "-" * 56)
    for snap in proj.snapshots:
        if snap.month in milestones:
            print(
                f"  {snap.month:<7} {fmt_mrr(snap.mrr):>10} "
                f"{fmt_mrr(snap.new_mrr):>9} {fmt_mrr(snap.churned_mrr):>9} "
                f"{fmt_mrr(snap.expansion_mrr):>8} {fmt_mrr(snap.net_new_mrr):>9}"
            )

    final = proj.snapshots[-1]
    growth_x = final.mrr / STARTING_MRR
    arr_final = final.mrr * 12
    weighted_cac = _weighted_cac(model.channel_mix)
    be = f"Month {proj.break_even_month}" if proj.break_even_month else f"> {SIMULATION_MONTHS}mo"

    print()
    print(f"  Final MRR ({SIMULATION_MONTHS}mo):    {fmt_mrr(final.mrr)}")
    print(f"  Final ARR:             {fmt_currency(arr_final)}")
    print(f"  Growth multiple:       {growth_x:.1f}x from starting MRR")
    print(f"  Weighted blended CAC:  {fmt_currency(weighted_cac)}")
    print(f"  Expected LTV:CAC:      {model.avg_ltv_cac:.1f}x")
    print(f"  Months to steady state:{model.months_to_steady_state}")
    print(f"  CAC break-even:        {be}")
