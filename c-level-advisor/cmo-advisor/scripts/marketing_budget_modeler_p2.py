# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from marketing_budget_modeler_base import *  # noqa: F403,E402
# fmt: off
from marketing_budget_modeler_p1 import ASP_ANNUAL, Channel, FUNNEL, LTV, MONTHLY_CHURN, ScenarioResult, TARGET_NEW_ARR, ltv_to_cac, score_channel  # noqa: E402,E501
# fmt: on


def allocate_mqls(
    channels: List[Channel],
    total_mqls_needed: int,
    budget_multiplier: float = 1.0,
) -> Tuple[Dict[str, int], Dict[str, float]]:
    """
    Allocate MQL targets across channels in priority order (best LTV:CAC first).
    budget_multiplier: 0.7 = conservative, 1.0 = moderate, 1.3 = aggressive.
    Returns (channel → MQLs, channel → budget).
    """
    ranked = sorted(channels, key=score_channel, reverse=True)
    remaining = total_mqls_needed
    channel_mqls: Dict[str, int] = {}
    channel_budget: Dict[str, float] = {}

    for ch in ranked:
        if remaining <= 0:
            channel_mqls[ch.name] = 0
            channel_budget[ch.name] = 0.0
            continue
        # Apply capacity ceiling scaled by multiplier (aggressive = push capacity)
        capacity = int(ch.max_mqls_per_month * 12 * budget_multiplier)
        allocated = min(remaining, capacity)
        channel_mqls[ch.name] = allocated
        channel_budget[ch.name] = allocated * ch.cac
        remaining -= allocated

    return channel_mqls, channel_budget
def build_scenario(
    name: str,
    channels: List[Channel],
    total_mqls: int,
    multiplier: float,
    notes: List[str],
) -> ScenarioResult:
    channel_mqls, channel_budget = allocate_mqls(channels, total_mqls, multiplier)

    total_budget = sum(channel_budget.values())
    total_mqls_allocated = sum(channel_mqls.values())
    projected_customers = math.floor(total_mqls_allocated * FUNNEL.mql_to_close)
    projected_arr = projected_customers * ASP_ANNUAL

    # Blended CAC = total budget / customers acquired
    blended_cac = total_budget / projected_customers if projected_customers > 0 else 0.0

    return ScenarioResult(
        name=name,
        total_budget=total_budget,
        channel_budgets=channel_budget,
        channel_mqls=channel_mqls,
        projected_customers=projected_customers,
        projected_arr=projected_arr,
        blended_cac=blended_cac,
        notes=notes,
    )
def fmt_currency(n: float) -> str:
    if n >= 1_000_000:
        return f"${n/1_000_000:.2f}M"
    if n >= 1_000:
        return f"${n/1_000:.1f}K"
    return f"${n:.0f}"
def fmt_ratio(n: float) -> str:
    return f"{n:.1f}x"
def print_header(title: str) -> None:
    width = 72
    print("\n" + "=" * width)
    print(f"  {title}")
    print("=" * width)
def print_channel_table(channels: List[Channel]) -> None:
    print_header("Channel Analysis — Current State")
    header = f"{'Channel':<25} {'CAC':>8} {'Payback':>9} {'LTV:CAC':>8} {'Cap/mo':>7} {'Trend':>10}"
    print(header)
    print("-" * 72)
    for ch in sorted(channels, key=score_channel, reverse=True):
        ratio = ltv_to_cac(ch.ltv, ch.cac)
        flag = ""
        if ratio < 1:
            flag = " ⚠ LOSS"
        elif ratio >= 6:
            flag = " ★ STRONG"
        elif ratio >= 3:
            flag = " ✓"
        print(
            f"{ch.name:<25} {fmt_currency(ch.cac):>8} "
            f"{ch.payback_months:>7.1f}mo {fmt_ratio(ratio):>8} "
            f"{ch.max_mqls_per_month:>7} {ch.trend:>10}{flag}"
        )
def print_funnel_summary(customers: int, mqls: int) -> None:
    print_header("Funnel Requirements")
    print(f"  Target new ARR:          {fmt_currency(TARGET_NEW_ARR)}")
    print(f"  Average selling price:   {fmt_currency(ASP_ANNUAL)}")
    print(f"  New customers needed:    {customers}")
    print(f"  Funnel MQL→Close rate:   {FUNNEL.mql_to_close:.1%}")
    print(f"  Total MQLs needed:       {mqls}")
    print(f"\n  Funnel stage rates:")
    print(f"    MQL → SAL:             {FUNNEL.mql_to_sal:.0%}")
    print(f"    SAL → SQL:             {FUNNEL.mql_to_sal * FUNNEL.sal_to_sql:.0%}")
    print(f"    SQL → Opportunity:     {FUNNEL.mql_to_sal * FUNNEL.sal_to_sql * FUNNEL.sql_to_opp:.0%}")
    print(f"    Opportunity → Close:   {FUNNEL.mql_to_close:.0%}")
    print(f"\n  LTV (estimated):         {fmt_currency(LTV)}")
    print(f"  Monthly churn:           {MONTHLY_CHURN:.1%}  ({MONTHLY_CHURN*12:.0%} annualized)")
