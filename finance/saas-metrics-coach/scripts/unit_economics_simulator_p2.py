# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from unit_economics_simulator_base import *  # noqa: F403,E402


def format_report(results):
    """Format simulation results as human-readable report."""
    lines = []
    lines.append("\n" + "=" * 70)
    lines.append("UNIT ECONOMICS SIMULATION - 12 MONTH PROJECTION")
    lines.append("=" * 70)
    
    # Inputs
    inputs = results["inputs"]
    lines.append("\n📊 INPUTS")
    lines.append(f"  Starting MRR: ${inputs['starting_mrr']:,.0f}")
    lines.append(f"  Monthly Growth: {inputs['monthly_growth_pct']}%")
    lines.append(f"  Monthly Churn: {inputs['monthly_churn_pct']}%")
    lines.append(f"  CAC: ${inputs['cac']:,.0f}")
    lines.append(f"  Gross Margin: {inputs['gross_margin']*100:.0f}%")
    lines.append(f"  S&M Spend: {inputs['sm_spend_pct']*100:.0f}% of revenue")
    
    # Summary
    summary = results["summary"]
    lines.append("\n📈 12-MONTH SUMMARY")
    lines.append(f"  Starting MRR: ${summary['starting_mrr']:,.0f}")
    lines.append(f"  Ending MRR: ${summary['ending_mrr']:,.0f}")
    lines.append(f"  Ending ARR: ${summary['ending_arr']:,.0f}")
    lines.append(f"  MRR Growth: {summary['mrr_growth_pct']:+.1f}%")
    lines.append(f"  Total Revenue: ${summary['total_revenue_12m']:,.0f}")
    lines.append(f"  Total Gross Profit: ${summary['total_gross_profit_12m']:,.0f}")
    lines.append(f"  Total S&M Spend: ${summary['total_sm_spend_12m']:,.0f}")
    lines.append(f"  Total Net Profit: ${summary['total_net_profit_12m']:,.0f}")
    
    # Monthly breakdown (first 3, last 3)
    lines.append("\n📅 MONTHLY PROJECTIONS")
    lines.append(f"{'Month':<8} {'MRR':<12} {'ARR':<12} {'Revenue':<12} {'Net Profit':<12}")
    lines.append("-" * 70)
    
    projs = results["projections"]
    for p in projs[:3]:
        lines.append(
            f"{p['month']:<8} ${p['mrr']:<11,.0f} ${p['arr']:<11,.0f} "
            f"${p['monthly_revenue']:<11,.0f} ${p['net_profit']:<11,.0f}"
        )
    
    if len(projs) > 6:
        lines.append("  ...")
    
    for p in projs[-3:]:
        lines.append(
            f"{p['month']:<8} ${p['mrr']:<11,.0f} ${p['arr']:<11,.0f} "
            f"${p['monthly_revenue']:<11,.0f} ${p['net_profit']:<11,.0f}"
        )
    
    lines.append("\n" + "=" * 70 + "\n")
    
    return "\n".join(lines)
