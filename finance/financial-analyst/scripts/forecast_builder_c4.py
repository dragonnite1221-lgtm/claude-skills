# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from forecast_builder_base import *  # noqa: F403,E402


class ForecastBuilderMixin4:
    def format_text(self, results: Dict[str, Any]) -> str:
        """Format forecast results as human-readable text."""
        lines: List[str] = []
        lines.append("=" * 70)
        lines.append("FINANCIAL FORECAST REPORT")
        lines.append("=" * 70)

        def fmt_money(val: float) -> str:
            if abs(val) >= 1e9:
                return f"${val / 1e9:,.2f}B"
            if abs(val) >= 1e6:
                return f"${val / 1e6:,.2f}M"
            if abs(val) >= 1e3:
                return f"${val / 1e3:,.1f}K"
            return f"${val:,.2f}"

        # Trend Analysis
        trend = results["trend_analysis"]
        if "error" not in trend:
            lines.append(f"\n--- TREND ANALYSIS ---")
            t = trend["trend"]
            lines.append(f"  Direction: {t['direction']}")
            lines.append(f"  R-squared: {t['r_squared']:.4f}")
            lines.append(
                f"  Average Historical Growth: "
                f"{trend['average_growth_rate'] * 100:.1f}%"
            )
            if trend["seasonality_index"]:
                lines.append(
                    f"  Seasonality Index (last 4): "
                    f"{', '.join(f'{s:.2f}' for s in trend['seasonality_index'])}"
                )

        # Scenario Comparison
        comp = results["scenario_comparison"]["comparison"]
        lines.append(f"\n--- SCENARIO COMPARISON ---")
        lines.append(
            f"  {'Scenario':<10s}  {'Revenue':>14s}  {'Op. Income':>14s}  "
            f"{'Growth':>8s}  {'Margin':>8s}"
        )
        lines.append("  " + "-" * 62)
        for c in comp:
            lines.append(
                f"  {c['scenario']:<10s}  {fmt_money(c['total_revenue']):>14s}  "
                f"{fmt_money(c['total_operating_income']):>14s}  "
                f"{c['growth_rate'] * 100:>7.1f}%  "
                f"{c['gross_margin'] * 100:>7.1f}%"
            )

        # Base scenario detail
        base = results["scenario_comparison"]["scenarios"].get("base", {})
        if base and base.get("forecast_periods"):
            lines.append(f"\n--- BASE CASE MONTHLY FORECAST ---")
            lines.append(
                f"  {'Period':>6s}  {'Revenue':>12s}  {'Gross Profit':>12s}  "
                f"{'Op. Income':>12s}"
            )
            lines.append("  " + "-" * 48)
            for p in base["forecast_periods"]:
                lines.append(
                    f"  {p['period']:>6d}  {fmt_money(p['revenue']):>12s}  "
                    f"{fmt_money(p['gross_profit']):>12s}  "
                    f"{fmt_money(p['operating_income']):>12s}"
                )

        # Cash Flow
        cf = results["rolling_cash_flow"]
        lines.append(f"\n--- 13-WEEK ROLLING CASH FLOW ---")
        lines.append(f"  Opening Balance: {fmt_money(cf['opening_balance'])}")
        lines.append(f"  Closing Balance: {fmt_money(cf['closing_balance'])}")
        lines.append(f"  Net Change:      {fmt_money(cf['net_change'])}")
        lines.append(
            f"  Minimum Balance: {fmt_money(cf['minimum_balance'])} "
            f"(Week {cf['minimum_balance_week']})"
        )
        if cf.get("cash_runway_weeks"):
            lines.append(f"  Cash Runway:     {cf['cash_runway_weeks']:.0f} weeks")

        lines.append(f"\n  Weekly Detail:")
        lines.append(
            f"  {'Wk':>3s}  {'Inflows':>10s}  {'Outflows':>10s}  "
            f"{'Net':>10s}  {'Balance':>12s}"
        )
        lines.append("  " + "-" * 50)
        for w in cf["weekly_projections"]:
            notes = f"  {w['notes']}" if w["notes"] else ""
            lines.append(
                f"  {w['week']:>3d}  {fmt_money(w['total_inflows']):>10s}  "
                f"{fmt_money(w['total_outflows']):>10s}  "
                f"{fmt_money(w['net_cash_flow']):>10s}  "
                f"{fmt_money(w['closing_balance']):>12s}{notes}"
            )

        lines.append("\n" + "=" * 70)
        return "\n".join(lines)
