# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from dcf_valuation_base import *  # noqa: F403,E402
from dcf_valuation_p0 import safe_divide  # noqa: F401,E501


class DCFModelMixin2:
    def sensitivity_analysis(
        self,
        wacc_range: Optional[List[float]] = None,
        growth_range: Optional[List[float]] = None,
    ) -> Dict[str, Any]:
        """
        Two-way sensitivity analysis: WACC vs terminal growth rate.

        Returns a table of enterprise values using nested lists (no numpy).
        """
        if wacc_range is None:
            base_wacc = self.wacc
            wacc_range = [
                round(base_wacc - 0.02, 4),
                round(base_wacc - 0.01, 4),
                round(base_wacc, 4),
                round(base_wacc + 0.01, 4),
                round(base_wacc + 0.02, 4),
            ]

        if growth_range is None:
            base_growth = self.assumptions.get("terminal_growth_rate", 0.025)
            growth_range = [
                round(base_growth - 0.01, 4),
                round(base_growth - 0.005, 4),
                round(base_growth, 4),
                round(base_growth + 0.005, 4),
                round(base_growth + 0.01, 4),
            ]

        rows = len(wacc_range)
        cols = len(growth_range)

        # Initialize sensitivity table as nested lists
        ev_table = [[0.0] * cols for _ in range(rows)]
        share_price_table = [[0.0] * cols for _ in range(rows)]

        terminal_fcf = self.projected_fcf[-1] if self.projected_fcf else 0

        for i, wacc_val in enumerate(wacc_range):
            for j, growth_val in enumerate(growth_range):
                if wacc_val <= growth_val:
                    ev_table[i][j] = float("inf")
                    share_price_table[i][j] = float("inf")
                    continue

                # Recalculate PV of projected FCFs with this WACC
                pv_fcf = 0.0
                for k, fcf in enumerate(self.projected_fcf):
                    pv_fcf += fcf / ((1 + wacc_val) ** (k + 1))

                # Terminal value with this growth rate
                tv = (terminal_fcf * (1 + growth_val)) / (wacc_val - growth_val)
                pv_tv = tv / ((1 + wacc_val) ** self.projection_years)

                ev = pv_fcf + pv_tv
                ev_table[i][j] = round(ev, 2)

                net_debt = self.historical.get("net_debt", 0)
                shares = self.historical.get("shares_outstanding", 1)
                equity = ev - net_debt
                share_price_table[i][j] = round(
                    safe_divide(equity, shares), 2
                )

        return {
            "wacc_values": wacc_range,
            "growth_values": growth_range,
            "enterprise_value_table": ev_table,
            "share_price_table": share_price_table,
        }
    def run_full_valuation(self) -> Dict[str, Any]:
        """Run the complete DCF valuation."""
        self.calculate_wacc()
        self.project_cash_flows()
        self.calculate_terminal_value()
        self.calculate_enterprise_value()
        self.calculate_equity_value()
        sensitivity = self.sensitivity_analysis()

        return {
            "wacc": self.wacc,
            "projected_revenue": self.projected_revenue,
            "projected_fcf": self.projected_fcf,
            "terminal_value": {
                "perpetuity_growth": self.terminal_value_perpetuity,
                "exit_multiple": self.terminal_value_exit_multiple,
            },
            "enterprise_value": {
                "perpetuity_growth": self.enterprise_value_perpetuity,
                "exit_multiple": self.enterprise_value_exit_multiple,
            },
            "equity_value": {
                "perpetuity_growth": self.equity_value_perpetuity,
                "exit_multiple": self.equity_value_exit_multiple,
            },
            "value_per_share": {
                "perpetuity_growth": self.value_per_share_perpetuity,
                "exit_multiple": self.value_per_share_exit_multiple,
            },
            "sensitivity_analysis": sensitivity,
        }
