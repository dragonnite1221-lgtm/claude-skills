# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from burn_rate_calculator_base import *  # noqa: F403,E402
# fmt: off
from burn_rate_calculator_p1 import HiringEntry, ModelConfig, MonthResult  # noqa: E402,E501
from burn_rate_calculator_p2 import RunwayCalculator, fmt_k  # noqa: E402,E501
# fmt: on


def print_summary(name: str, results: list[MonthResult], calc: RunwayCalculator) -> None:
    cash_out = calc.cash_out_date(results)
    bm = calc.burn_multiple(results)
    last = results[-1]
    first = results[0]

    print(f"\n{'='*60}")
    print(f"  SCENARIO: {name}")
    print(f"{'='*60}")
    print(f"  Months modeled:    {len(results)}")
    print(f"  Cash out:          {cash_out or 'Does not run out in model period'}")
    print(f"  Ending cash:       {fmt_k(last.cash_end)}")
    print(f"  Final runway:      {last.runway_months:.1f} months")
    print(f"  Starting MRR:      {fmt_k(first.mrr)}")
    print(f"  Ending MRR:        {fmt_k(last.mrr)}")
    print(f"  Ending headcount:  {last.headcount}")
    print(f"  Burn multiple:     {bm:.2f}x")
    print(f"  Avg net burn:      {fmt_k(sum(r.net_burn for r in results)/len(results))}/mo")

    # Decision triggers
    print(f"\n  Decision Triggers:")
    triggers = {9: "⚠️  START FUNDRAISE", 6: "🔴 COST REDUCTION PLAN", 4: "🚨 EXECUTE CUTS / BRIDGE"}
    shown = set()
    for r in results:
        for threshold, label in triggers.items():
            if r.runway_months <= threshold and threshold not in shown:
                print(f"    {r.label}: {label} (runway = {r.runway_months:.1f} mo)")
                shown.add(threshold)
def print_monthly_table(results: list[MonthResult], max_rows: int = 24) -> None:
    header = f"{'Month':<22} {'MRR':>10} {'Hdct':>6} {'Net Burn':>12} {'Cash':>12} {'Runway':>8}"
    print(f"\n{header}")
    print("-" * len(header))
    for r in results[:max_rows]:
        runway_str = f"{r.runway_months:.1f}mo" if r.runway_months != float("inf") else "∞"
        print(
            f"{r.label:<22} "
            f"{fmt_k(r.mrr):>10} "
            f"{r.headcount:>6} "
            f"{fmt_k(r.net_burn):>12} "
            f"{fmt_k(r.cash_end):>12} "
            f"{runway_str:>8}"
        )
def export_csv(scenarios: list[tuple[str, list[MonthResult]]]) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow([
        "Scenario", "Month", "Label", "MRR", "Gross Profit", "Headcount",
        "Headcount Cost", "Other Opex", "Gross Burn", "Net Burn",
        "Cash Start", "Cash End", "Runway Months"
    ])
    for name, results in scenarios:
        for r in results:
            writer.writerow([
                name, r.month, r.label,
                round(r.mrr, 2), round(r.gross_profit, 2), r.headcount,
                round(r.headcount_cost, 2), round(r.other_opex, 2),
                round(r.gross_burn, 2), round(r.net_burn, 2),
                round(r.cash_start, 2), round(r.cash_end, 2),
                round(r.runway_months, 2),
            ])
    return buf.getvalue()
def make_sample_configs() -> list[ModelConfig]:
    """
    Sample company: Series A SaaS startup
      - $3M cash on hand (post Series A)
      - $125K MRR (~$1.5M ARR)
      - 18 employees, $150K avg salary
      - $80K/mo non-headcount opex (infra, tools, office)
      - 72% gross margin
    """
    common_kwargs = dict(
        starting_cash=3_000_000,
        starting_mrr=125_000,
        starting_headcount=18,
        avg_loaded_salary=150_000,
        base_non_headcount_opex=80_000,
        gross_margin_pct=0.72,
        model_months=24,
        start_date=date(2025, 1, 1),
    )

    # Base: 10% MoM growth, moderate hiring
    base_hiring = [
        HiringEntry(month=2,  role="AE #1",         department="sales",       annual_salary=120_000, recruiting_cost=18_000),
        HiringEntry(month=3,  role="Senior SWE #1",  department="engineering", annual_salary=160_000, recruiting_cost=24_000),
        HiringEntry(month=5,  role="SDR #1",         department="sales",       annual_salary=80_000,  recruiting_cost=12_000),
        HiringEntry(month=6,  role="CSM #1",         department="cs",          annual_salary=90_000,  recruiting_cost=13_500),
        HiringEntry(month=8,  role="AE #2",          department="sales",       annual_salary=120_000, recruiting_cost=18_000),
        HiringEntry(month=9,  role="Senior SWE #2",  department="engineering", annual_salary=165_000, recruiting_cost=24_750),
        HiringEntry(month=12, role="Controller",     department="ga",          annual_salary=130_000, recruiting_cost=19_500),
        HiringEntry(month=14, role="AE #3",          department="sales",       annual_salary=125_000, recruiting_cost=18_750),
        HiringEntry(month=15, role="ML Engineer",    department="engineering", annual_salary=175_000, recruiting_cost=26_250),
        HiringEntry(month=18, role="AE #4",          department="sales",       annual_salary=125_000, recruiting_cost=18_750),
    ]

    # Bull: 15% MoM growth, full hiring plan
    bull_hiring = base_hiring + [
        HiringEntry(month=4,  role="Marketing Manager", department="sales",       annual_salary=110_000, recruiting_cost=16_500),
        HiringEntry(month=7,  role="Senior SWE #3",     department="engineering", annual_salary=165_000, recruiting_cost=24_750),
        HiringEntry(month=10, role="AE #5",              department="sales",       annual_salary=125_000, recruiting_cost=18_750),
        HiringEntry(month=13, role="DevOps Engineer",    department="engineering", annual_salary=150_000, recruiting_cost=22_500),
        HiringEntry(month=16, role="AE #6",              department="sales",       annual_salary=125_000, recruiting_cost=18_750),
    ]

    # Bear: 5% MoM growth, hiring freeze after month 3
    bear_hiring = [
        HiringEntry(month=2, role="AE #1",        department="sales",       annual_salary=120_000, recruiting_cost=18_000),
        HiringEntry(month=3, role="Senior SWE #1", department="engineering", annual_salary=160_000, recruiting_cost=24_000),
    ]

    return [
        ModelConfig(name="BULL  (15% MoM, full hiring)",       mrr_growth_rate=0.15, hiring_plan=bull_hiring,  **common_kwargs),
        ModelConfig(name="BASE  (10% MoM, planned hiring)",     mrr_growth_rate=0.10, hiring_plan=base_hiring,  **common_kwargs),
        ModelConfig(name="BEAR  ( 5% MoM, hiring freeze M3+)", mrr_growth_rate=0.05, hiring_plan=bear_hiring,  **common_kwargs),
        ModelConfig(name="DISTRESS (0% growth, freeze now)",    mrr_growth_rate=0.00, hiring_plan=[],           **common_kwargs),
    ]
