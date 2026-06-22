# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from revenue_forecast_model_base import *  # noqa: F403,E402
# fmt: off
from revenue_forecast_model_p3 import fmt_currency, fmt_pct, print_header, print_section  # noqa: E402,E501
# fmt: on


def print_report(engine, quota=None, current_quarter=None):
    open_deals = engine.open_deals()
    won_deals = engine.closed_won_deals()

    print_header("REVENUE FORECAST MODEL")
    print(f"  Generated: {date.today().isoformat()}")
    print(f"  Open deals: {len(open_deals)}")
    print(f"  Closed Won (in dataset): {len(won_deals)}")
    total_pipeline = sum(d.arr_value for d in open_deals)
    total_won = sum(d.arr_value for d in won_deals)
    print(f"  Total open pipeline: {fmt_currency(total_pipeline)}")
    print(f"  Total closed won:    {fmt_currency(total_won)}")

    # ── Coverage ratio
    if quota:
        print_section("PIPELINE COVERAGE")
        q = current_quarter or "this quarter"
        ratio = engine.coverage_ratio(quota, period_filter=current_quarter)
        status = "✅ Healthy" if ratio >= 3.0 else ("⚠️  Thin" if ratio >= 2.0 else "🔴 Critical")
        print(f"  Quota target:    {fmt_currency(quota)}")
        print(f"  Coverage ratio:  {ratio:.1f}x  {status}")
        print(f"  (Minimum healthy = 3x; < 2x = pipeline emergency)")

    # ── Stage distribution
    print_section("STAGE DISTRIBUTION")
    stage_dist = engine.stage_distribution()
    col_w = [28, 8, 14, 12, 10]
    header = f"  {'Stage':<{col_w[0]}} {'Deals':>{col_w[1]}} {'Pipeline':>{col_w[2]}} {'Avg Size':>{col_w[3]}} {'Win Prob':>{col_w[4]}}"
    print(header)
    print("  " + "-" * (sum(col_w) + 4))
    for stage, data in sorted(stage_dist.items(), key=lambda x: -x[1]["total_arr"]):
        print(f"  {stage:<{col_w[0]}} {data['count']:>{col_w[1]}} "
              f"{fmt_currency(data['total_arr']):>{col_w[2]}} "
              f"{fmt_currency(data['avg_arr']):>{col_w[3]}} "
              f"{fmt_pct(data['probability']):>{col_w[4]}}")

    # ── Scenario forecast by month
    print_section("MONTHLY FORECAST — ALL SCENARIOS")
    summaries = engine.scenario_summary()
    col_w2 = [10, 8, 14, 14, 14, 14]
    h2 = (f"  {'Month':<{col_w2[0]}} {'Deals':>{col_w2[1]}} "
          f"{'Pipeline':>{col_w2[2]}} {'Conservative':>{col_w2[3]}} "
          f"{'Base':>{col_w2[4]}} {'Upside':>{col_w2[5]}}")
    print(h2)
    print("  " + "-" * (sum(col_w2) + 5))
    for month, data in summaries.items():
        print(f"  {month:<{col_w2[0]}} {data['deal_count']:>{col_w2[1]}} "
              f"{fmt_currency(data['open_pipeline']):>{col_w2[2]}} "
              f"{fmt_currency(data['conservative']):>{col_w2[3]}} "
              f"{fmt_currency(data['base']):>{col_w2[4]}} "
              f"{fmt_currency(data['upside']):>{col_w2[5]}}")

    # ── Quarterly rollup
    print_section("QUARTERLY FORECAST ROLLUP")
    q_conservative = defaultdict(float)
    q_base = defaultdict(float)
    q_upside = defaultdict(float)
    q_pipeline = defaultdict(float)
    q_count = defaultdict(int)
    for deal in open_deals:
        q_conservative[deal.quarter] += deal.weighted_value(engine.stage_probs, "conservative")
        q_base[deal.quarter] += deal.weighted_value(engine.stage_probs, "base")
        q_upside[deal.quarter] += deal.weighted_value(engine.stage_probs, "upside")
        q_pipeline[deal.quarter] += deal.arr_value
        q_count[deal.quarter] += 1

    quarters = sorted(q_base.keys())
    col_w3 = [10, 8, 14, 14, 14, 14]
    h3 = (f"  {'Quarter':<{col_w3[0]}} {'Deals':>{col_w3[1]}} "
          f"{'Pipeline':>{col_w3[2]}} {'Conservative':>{col_w3[3]}} "
          f"{'Base':>{col_w3[4]}} {'Upside':>{col_w3[5]}}")
    print(h3)
    print("  " + "-" * (sum(col_w3) + 5))
    for q in quarters:
        print(f"  {q:<{col_w3[0]}} {q_count[q]:>{col_w3[1]}} "
              f"{fmt_currency(q_pipeline[q]):>{col_w3[2]}} "
              f"{fmt_currency(q_conservative[q]):>{col_w3[3]}} "
              f"{fmt_currency(q_base[q]):>{col_w3[4]}} "
              f"{fmt_currency(q_upside[q]):>{col_w3[5]}}")

    # ── Monte Carlo confidence interval
    print_section("CONFIDENCE INTERVAL (Monte Carlo, 1,000 simulations)")
    p10, p50, p90 = engine.confidence_interval("base")
    print(f"  P10 (conservative floor): {fmt_currency(p10)}")
    print(f"  P50 (median expected):    {fmt_currency(p50)}")
    print(f"  P90 (upside ceiling):     {fmt_currency(p90)}")
    print(f"  Range spread: {fmt_currency(p90 - p10)}")

    # ── Rep performance
    print_section("REP PIPELINE PERFORMANCE")
    rep_perf = engine.rep_performance()
    if rep_perf:
        col_w4 = [20, 8, 14, 14, 12]
        h4 = (f"  {'Rep':<{col_w4[0]}} {'Deals':>{col_w4[1]}} "
              f"{'Pipeline':>{col_w4[2]}} {'Weighted':>{col_w4[3]}} {'Avg Size':>{col_w4[4]}}")
        print(h4)
        print("  " + "-" * (sum(col_w4) + 4))
        for rep, data in sorted(rep_perf.items(), key=lambda x: -x[1]["pipeline"]):
            print(f"  {rep:<{col_w4[0]}} {data['deal_count']:>{col_w4[1]}} "
                  f"{fmt_currency(data['pipeline']):>{col_w4[2]}} "
                  f"{fmt_currency(data['weighted_base']):>{col_w4[3]}} "
                  f"{fmt_currency(data['avg_deal_size']):>{col_w4[4]}}")

    # ── Segment breakdown
    print_section("SEGMENT BREAKDOWN (Base Forecast)")
    seg = engine.segment_breakdown("base")
    for segment, value in sorted(seg.items(), key=lambda x: -x[1]):
        bar_len = int((value / total_pipeline) * 30) if total_pipeline else 0
        bar = "█" * bar_len
        print(f"  {segment:<20} {fmt_currency(value):>12}  {bar}")

    # ── Red flags
    print_section("FORECAST HEALTH FLAGS")
    flags = []
    if total_pipeline > 0:
        coverage = total_pipeline / quota if quota else None
        if coverage and coverage < 2.0:
            flags.append("🔴 Pipeline coverage below 2x — serious shortfall risk this quarter")
        elif coverage and coverage < 3.0:
            flags.append("⚠️  Pipeline coverage below 3x — limited buffer for slippage")

        # Stage concentration risk
        early_stage_pct = sum(
            d.arr_value for d in open_deals
            if engine.stage_probs.get(d.stage, 0) < 0.30
        ) / total_pipeline
        if early_stage_pct > 0.60:
            flags.append(f"⚠️  {fmt_pct(early_stage_pct)} of pipeline in early stages (< 30% probability)")

        # Deal concentration
        deal_values = sorted([d.arr_value for d in open_deals], reverse=True)
        if deal_values and deal_values[0] / total_pipeline > 0.25:
            flags.append(f"⚠️  Top deal is {fmt_pct(deal_values[0]/total_pipeline)} of pipeline — concentration risk")

        # Spread between scenarios
        total_conservative = sum(d.weighted_value(engine.stage_probs, "conservative") for d in open_deals)
        total_upside = sum(d.weighted_value(engine.stage_probs, "upside") for d in open_deals)
        spread = (total_upside - total_conservative) / total_conservative if total_conservative else 0
        if spread > 0.40:
            flags.append(f"⚠️  High scenario spread ({fmt_pct(spread)}) — forecast confidence is low")

    if flags:
        for f in flags:
            print(f"  {f}")
    else:
        print("  ✅ No critical flags detected")

    print()
