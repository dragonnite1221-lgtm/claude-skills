# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from dcf_valuation_base import *  # noqa: F403,E402


class DCFModelMixin3:
    def format_text(self, results: Dict[str, Any]) -> str:
        """Format valuation results as human-readable text."""
        lines: List[str] = []
        lines.append("=" * 70)
        lines.append("DCF VALUATION ANALYSIS")
        lines.append("=" * 70)

        def fmt_money(val: float) -> str:
            if val == float("inf"):
                return "N/A (WACC <= growth)"
            if abs(val) >= 1e9:
                return f"${val / 1e9:,.2f}B"
            if abs(val) >= 1e6:
                return f"${val / 1e6:,.2f}M"
            if abs(val) >= 1e3:
                return f"${val / 1e3:,.1f}K"
            return f"${val:,.2f}"

        lines.append(f"\n--- WACC ---")
        lines.append(f"  Weighted Average Cost of Capital: {results['wacc'] * 100:.2f}%")

        lines.append(f"\n--- REVENUE PROJECTIONS ---")
        for i, rev in enumerate(results["projected_revenue"], 1):
            lines.append(f"  Year {i}: {fmt_money(rev)}")

        lines.append(f"\n--- FREE CASH FLOW PROJECTIONS ---")
        for i, fcf in enumerate(results["projected_fcf"], 1):
            lines.append(f"  Year {i}: {fmt_money(fcf)}")

        lines.append(f"\n--- TERMINAL VALUE ---")
        lines.append(
            f"  Perpetuity Growth Method: "
            f"{fmt_money(results['terminal_value']['perpetuity_growth'])}"
        )
        lines.append(
            f"  Exit Multiple Method:     "
            f"{fmt_money(results['terminal_value']['exit_multiple'])}"
        )

        lines.append(f"\n--- ENTERPRISE VALUE ---")
        lines.append(
            f"  Perpetuity Growth Method: "
            f"{fmt_money(results['enterprise_value']['perpetuity_growth'])}"
        )
        lines.append(
            f"  Exit Multiple Method:     "
            f"{fmt_money(results['enterprise_value']['exit_multiple'])}"
        )

        lines.append(f"\n--- EQUITY VALUE ---")
        lines.append(
            f"  Perpetuity Growth Method: "
            f"{fmt_money(results['equity_value']['perpetuity_growth'])}"
        )
        lines.append(
            f"  Exit Multiple Method:     "
            f"{fmt_money(results['equity_value']['exit_multiple'])}"
        )

        lines.append(f"\n--- VALUE PER SHARE ---")
        vps = results["value_per_share"]
        lines.append(f"  Perpetuity Growth Method: ${vps['perpetuity_growth']:,.2f}")
        lines.append(f"  Exit Multiple Method:     ${vps['exit_multiple']:,.2f}")

        # Sensitivity table
        sens = results["sensitivity_analysis"]
        lines.append(f"\n--- SENSITIVITY ANALYSIS (Enterprise Value) ---")
        lines.append(f"  WACC vs Terminal Growth Rate")
        lines.append("")

        header = "  {:>10s}".format("WACC \\ g")
        for g in sens["growth_values"]:
            header += f"  {g * 100:>8.1f}%"
        lines.append(header)
        lines.append("  " + "-" * (10 + 10 * len(sens["growth_values"])))

        for i, w in enumerate(sens["wacc_values"]):
            row = f"  {w * 100:>9.1f}%"
            for j in range(len(sens["growth_values"])):
                val = sens["enterprise_value_table"][i][j]
                if val == float("inf"):
                    row += f"  {'N/A':>8s}"
                else:
                    row += f"  {fmt_money(val):>8s}"
            lines.append(row)

        lines.append("\n" + "=" * 70)
        return "\n".join(lines)
