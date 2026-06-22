# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from unit_economics_analyzer_base import *  # noqa: F403,E402
# fmt: off
from unit_economics_analyzer_p1 import ChannelData, UnitEconomicsResult, calc_payback  # noqa: E402,E501
from unit_economics_analyzer_p2 import blended_cac, blended_ltv, fmt, pct  # noqa: E402,E501
# fmt: on


def rating(ltv_cac: float, payback: float) -> str:
    if ltv_cac == float("inf"):
        return "∞"
    if ltv_cac >= 5 and payback <= 12:
        return "🟢 Excellent"
    if ltv_cac >= 3 and payback <= 18:
        return "🟡 Good"
    if ltv_cac >= 2 and payback <= 24:
        return "🟠 Marginal"
    return "🔴 Poor"
def print_cohort_analysis(results: list[UnitEconomicsResult]) -> None:
    print("\n" + "="*80)
    print("  COHORT ANALYSIS")
    print("="*80)
    print(f"  {'Cohort':<12} {'Cust':>5} {'CAC':>8} {'ARPA/mo':>9} {'Churn/mo':>10} "
          f"{'LTV':>10} {'LTV:CAC':>8} {'Payback':>9} {'Ret@M12':>8}")
    print("  " + "-"*88)
    for r in results:
        payback_str = f"{r.payback_months:.1f}mo" if r.payback_months != float("inf") else "∞"
        ltv_str = fmt(r.ltv) if r.ltv != float("inf") else "∞"
        ltv_cac_str = f"{r.ltv_cac_ratio:.1f}x" if r.ltv_cac_ratio != float("inf") else "∞"
        print(
            f"  {r.label:<12} {r.customers:>5} {fmt(r.cac):>8} {fmt(r.arpa):>9} "
            f"{pct(r.monthly_churn):>10} {ltv_str:>10} {ltv_cac_str:>8} "
            f"{payback_str:>9} {pct(r.retention_m12):>8}"
        )

    # Trend analysis
    print("\n  Cohort Trend (is the business getting better or worse?):")
    if len(results) >= 3:
        ltv_cac_values = [r.ltv_cac_ratio for r in results if r.ltv_cac_ratio != float("inf")]
        cac_values = [r.cac for r in results]
        churn_values = [r.monthly_churn for r in results]

        if len(ltv_cac_values) >= 2:
            ltv_cac_trend = "↑ Improving" if ltv_cac_values[-1] > ltv_cac_values[0] else "↓ Deteriorating"
        else:
            ltv_cac_trend = "n/a"

        cac_trend = "↓ Decreasing (good)" if cac_values[-1] < cac_values[0] else "↑ Increasing"
        churn_trend = "↓ Improving" if churn_values[-1] < churn_values[0] else "↑ Worsening"

        print(f"    LTV:CAC:    {ltv_cac_trend}")
        print(f"    CAC:        {cac_trend}")
        print(f"    Churn rate: {churn_trend}")
def print_channel_analysis(results: list[UnitEconomicsResult], channels: list[ChannelData]) -> None:
    print("\n" + "="*80)
    print("  CHANNEL ANALYSIS (Per-Channel vs Blended)")
    print("="*80)
    print(f"  {'Channel':<22} {'Spend':>9} {'Cust':>5} {'CAC':>8} {'LTV':>10} {'LTV:CAC':>8} {'Payback':>9} {'Rating'}")
    print("  " + "-"*90)
    for r, ch in zip(results, channels):
        payback_str = f"{r.payback_months:.1f}mo" if r.payback_months != float("inf") else "∞"
        ltv_str = fmt(r.ltv) if r.ltv != float("inf") else "∞"
        ltv_cac_str = f"{r.ltv_cac_ratio:.1f}x" if r.ltv_cac_ratio != float("inf") else "∞"
        print(
            f"  {r.label:<22} {fmt(ch.spend):>9} {r.customers:>5} {fmt(r.cac):>8} "
            f"{ltv_str:>10} {ltv_cac_str:>8} {payback_str:>9}  {rating(r.ltv_cac_ratio, r.payback_months)}"
        )

    # Blended comparison
    b_cac = blended_cac(channels)
    b_ltv = blended_ltv(channels)
    b_ltv_cac = b_ltv / b_cac if b_cac > 0 else 0
    total_spend = sum(c.spend for c in channels)
    total_customers = sum(c.customers_acquired for c in channels)
    avg_payback = sum(
        calc_payback(b_cac, c.avg_arpa, c.gross_margin_pct) * c.customers_acquired
        for c in channels
    ) / total_customers

    print("  " + "-"*90)
    print(
        f"  {'BLENDED (dangerous)':<22} {fmt(total_spend):>9} {total_customers:>5} "
        f"{fmt(b_cac):>8} {fmt(b_ltv):>10} {b_ltv_cac:.1f}x{'':<7} "
        f"{avg_payback:.1f}mo{'':<4}  {rating(b_ltv_cac, avg_payback)}"
    )
    print("\n  ⚠️  Blended numbers hide channel-level problems. Manage channels individually.")

    # Budget reallocation
    print("\n  Recommended Budget Reallocation:")
    sorted_results = sorted(zip(results, channels), key=lambda x: x[0].ltv_cac_ratio, reverse=True)
    for r, ch in sorted_results:
        if r.ltv_cac_ratio >= 3:
            action = "✅ Scale"
        elif r.ltv_cac_ratio >= 2:
            action = "🔄 Optimize"
        else:
            action = "❌ Cut / pause"
        print(f"    {ch.channel:<22} LTV:CAC = {r.ltv_cac_ratio:.1f}x  → {action}")
def export_csv_results(cohort_results: list[UnitEconomicsResult], channel_results: list[UnitEconomicsResult]) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["Type", "Label", "Customers", "CAC", "ARPA_Monthly", "Gross_Margin_Pct",
                     "Monthly_Churn", "LTV", "LTV_CAC_Ratio", "Payback_Months",
                     "Retention_M6", "Retention_M12"])
    for r in cohort_results:
        writer.writerow(["cohort", r.label, r.customers, round(r.cac, 2), round(r.arpa, 2),
                         r.gross_margin_pct, round(r.monthly_churn, 4),
                         round(r.ltv, 2) if r.ltv != float("inf") else "inf",
                         round(r.ltv_cac_ratio, 2) if r.ltv_cac_ratio != float("inf") else "inf",
                         round(r.payback_months, 2) if r.payback_months != float("inf") else "inf",
                         round(r.retention_m6, 3) if r.retention_m6 else "",
                         round(r.retention_m12, 3) if r.retention_m12 else ""])
    for r in channel_results:
        writer.writerow(["channel", r.label, r.customers, round(r.cac, 2), round(r.arpa, 2),
                         r.gross_margin_pct, round(r.monthly_churn, 4),
                         round(r.ltv, 2) if r.ltv != float("inf") else "inf",
                         round(r.ltv_cac_ratio, 2) if r.ltv_cac_ratio != float("inf") else "inf",
                         round(r.payback_months, 2) if r.payback_months != float("inf") else "inf",
                         "", ""])
    return buf.getvalue()
