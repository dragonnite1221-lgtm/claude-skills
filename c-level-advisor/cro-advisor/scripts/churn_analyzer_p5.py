# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from churn_analyzer_base import *  # noqa: F403,E402
# fmt: off
from churn_analyzer_p2 import RetentionAnalyzer  # noqa: E402,E501
from churn_analyzer_p3 import CohortAnalyzer  # noqa: E402,E501
from churn_analyzer_p4 import ExpansionAnalyzer, fmt_currency, fmt_pct, grr_status, nrr_status, print_header, print_section  # noqa: E402,E501
# fmt: on


def print_full_report(customers, period_start, period_end):
    analyzer = RetentionAnalyzer(customers, as_of=period_end)
    cohort_analyzer = CohortAnalyzer(customers)
    expansion_analyzer = ExpansionAnalyzer(customers)

    print_header("CHURN & RETENTION ANALYZER")
    print(f"  Analysis period: {period_start.isoformat()} → {period_end.isoformat()}")
    print(f"  Total customers in dataset: {len(customers)}")
    active = analyzer.active_customers(period_end)
    churned_in_period = analyzer.churned_customers(period_start, period_end)
    print(f"  Active at period end: {len(active)}")
    print(f"  Churned in period:    {len(churned_in_period)}")

    # ── ARR Waterfall
    print_section("ARR WATERFALL")
    wf = analyzer.arr_waterfall(period_start, period_end)
    print(f"  Opening ARR:           {fmt_currency(wf['opening_arr'])}")
    print(f"  + New Logo ARR:       +{fmt_currency(wf['new_arr'])}")
    print(f"  + Expansion ARR:      +{fmt_currency(wf['expansion_arr'])}")
    print(f"  - Contraction ARR:    -{fmt_currency(wf['contraction_arr'])}")
    print(f"  - Churned ARR:        -{fmt_currency(wf['churned_arr'])}")
    print(f"  {'─'*42}")
    print(f"  Closing ARR:           {fmt_currency(wf['closing_arr'])}")
    print(f"  Net New ARR:          {'+' if wf['net_new_arr'] >= 0 else ''}{fmt_currency(wf['net_new_arr'])}")

    # ── NRR / GRR
    print_section("RETENTION METRICS")
    nrr = wf["nrr"]
    grr = wf["grr"]
    logo_churn = analyzer.logo_churn_rate(period_start, period_end)
    rev_churn = analyzer.revenue_churn_rate(period_start, period_end)

    print(f"  NRR (Net Revenue Retention):   {fmt_pct(nrr)}   {nrr_status(nrr)}")
    print(f"  GRR (Gross Revenue Retention): {fmt_pct(grr)}   {grr_status(grr)}")
    print(f"  Logo Churn Rate (period):      {fmt_pct(logo_churn)}")
    print(f"  Revenue Churn Rate (period):   {fmt_pct(rev_churn)}")
    if wf["opening_arr"] > 0:
        expansion_rate = wf["expansion_arr"] / wf["opening_arr"]
        print(f"  Expansion Rate (period):       {fmt_pct(expansion_rate)}")
    print()
    print(f"  NRR Benchmark: >120% world-class | 100-120% healthy | <100% fix immediately")

    # ── Expansion summary
    print_section("EXPANSION REVENUE")
    exp = expansion_analyzer.expansion_summary()
    print(f"  Expanding customers:  {exp['expanding_count']} / {exp['active_customers']} ({fmt_pct(exp['expanding_count']/exp['active_customers']) if exp['active_customers'] else '—'})")
    print(f"  Contracting:          {exp['contracting_count']} / {exp['active_customers']}")
    print(f"  Expansion ARR:        {fmt_currency(exp['expansion_arr'])} ({fmt_pct(exp['expansion_rate'])} of base)")
    print(f"  Contraction ARR:      {fmt_currency(exp['contraction_arr'])}")
    print(f"  Net Expansion Rate:   {fmt_pct(exp['net_expansion_rate'])}")

    # ── Segment breakdown
    print_section("SEGMENT BREAKDOWN (NRR Components)")
    seg_data = expansion_analyzer.expansion_by_segment()
    col_w = [18, 8, 12, 10, 10, 10]
    h = (f"  {'Segment':<{col_w[0]}} {'Custs':>{col_w[1]}} {'ARR':>{col_w[2]}} "
         f"{'Expansion':>{col_w[3]}} {'Contraction':>{col_w[4]}} {'NRR':>{col_w[5]}}")
    print(h)
    print("  " + "-" * (sum(col_w) + 5))
    for seg, data in sorted(seg_data.items(), key=lambda x: -x[1]["arr"]):
        print(f"  {seg:<{col_w[0]}} {data['customer_count']:>{col_w[1]}} "
              f"{fmt_currency(data['arr']):>{col_w[2]}} "
              f"{fmt_currency(data['expansion_arr']):>{col_w[3]}} "
              f"{fmt_currency(data['contraction_arr']):>{col_w[4]}} "
              f"{fmt_pct(data['net_nrr_contribution']):>{col_w[5]}}")

    # ── Cohort retention
    print_section("COHORT RETENTION CURVES")
    cohort_report = cohort_analyzer.cohort_report()
    print(f"  {'Cohort':<10} {'Custs':>6} {'Opening ARR':>13} {'Mo.3':>8} {'Mo.6':>8} {'Mo.12':>8}")
    print("  " + "-" * 57)
    for cohort, data in cohort_report.items():
        curve = data["retention_curve"]
        m3 = fmt_pct(curve[3]) if 3 in curve else "  —"
        m6 = fmt_pct(curve[6]) if 6 in curve else "  —"
        m12 = fmt_pct(curve[12]) if 12 in curve else "  —"
        print(f"  {cohort:<10} {data['customer_count']:>6} "
              f"{fmt_currency(data['opening_arr']):>13} "
              f"{m3:>8} {m6:>8} {m12:>8}")

    # ── At-risk accounts
    print_section("AT-RISK ACCOUNTS")
    at_risk = cohort_analyzer.identify_at_risk()
    if at_risk:
        print(f"  {'Customer':<22} {'Segment':<14} {'ARR':>10} {'Tenure':>8} {'Risk':>6}  Reason")
        print("  " + "-" * 80)
        for acct in at_risk[:10]:  # Top 10
            reason_short = acct["risk_reasons"][0] if acct["risk_reasons"] else ""
            tenure_str = f"{acct['tenure_months']}mo"
            print(f"  {acct['name']:<22} {acct['segment']:<14} "
                  f"{fmt_currency(acct['arr']):>10} {tenure_str:>8} "
                  f"{acct['risk_score']:>5}  {reason_short}")
        if len(at_risk) > 10:
            print(f"  ... and {len(at_risk) - 10} more at-risk accounts")
    else:
        print("  ✅ No at-risk accounts identified")

    # ── Expansion candidates
    print_section("EXPANSION CANDIDATES (no expansion yet, healthy tenure)")
    candidates = expansion_analyzer.top_expansion_candidates()
    if candidates:
        print(f"  {'Customer':<22} {'Segment':<14} {'ARR':>10} {'Tenure':>8}  Action")
        print("  " + "-" * 70)
        for c in candidates[:8]:
            action = "Upsell review" if c["arr"] > 20000 else "Seat expansion call"
            tenure_str = f"{c['tenure_months']}mo"
            print(f"  {c['name']:<22} {c['segment']:<14} "
                  f"{fmt_currency(c['arr']):>10} {tenure_str:>8}  {action}")
    else:
        print("  ✅ All eligible accounts have expansion in motion")

    # ── Red flags
    print_section("HEALTH FLAGS")
    flags = []
    if nrr < 1.0:
        flags.append("🔴 NRR below 100% — revenue base is shrinking. Fix before scaling sales.")
    if grr < 0.85:
        flags.append(f"🔴 GRR {fmt_pct(grr)} — gross retention below 85% threshold. Churn is a product/CS problem.")
    if logo_churn > 0.05:
        flags.append(f"⚠️  Logo churn {fmt_pct(logo_churn)} this period — run cohort analysis to find the pattern.")
    if exp["expansion_rate"] < 0.10 and exp["active_customers"] > 10:
        flags.append("⚠️  Expansion rate below 10% — upsell motion is weak or non-existent.")
    churned_arr_pct = wf["churned_arr"] / wf["opening_arr"] if wf["opening_arr"] else 0
    if churned_arr_pct > 0.10:
        flags.append(f"🔴 Revenue churn at {fmt_pct(churned_arr_pct)} of opening ARR this period — high urgency.")
    if len(at_risk) > len(active) * 0.20:
        flags.append(f"⚠️  {len(at_risk)} of {len(active)} active accounts flagged at-risk ({fmt_pct(len(at_risk)/len(active) if active else 0)})")

    if flags:
        for f in flags:
            print(f"  {f}")
    else:
        print("  ✅ No critical health flags")

    print()
