# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from dcf_valuation_base import *  # noqa: F403,E402
from dcf_valuation_p0 import safe_divide  # noqa: F401,E501


class DCFModelMixin1:
    def calculate_enterprise_value(self) -> Tuple[float, float]:
        """Calculate enterprise value by discounting projected FCFs and terminal value."""
        if not self.projected_fcf:
            raise ValueError("Must project cash flows first")

        # Discount projected FCFs
        pv_fcf = 0.0
        for i, fcf in enumerate(self.projected_fcf):
            discount_factor = (1 + self.wacc) ** (i + 1)
            pv_fcf += fcf / discount_factor

        # Discount terminal values
        terminal_discount = (1 + self.wacc) ** self.projection_years

        pv_tv_perpetuity = self.terminal_value_perpetuity / terminal_discount
        pv_tv_exit = self.terminal_value_exit_multiple / terminal_discount

        self.enterprise_value_perpetuity = pv_fcf + pv_tv_perpetuity
        self.enterprise_value_exit_multiple = pv_fcf + pv_tv_exit

        return self.enterprise_value_perpetuity, self.enterprise_value_exit_multiple
    def calculate_equity_value(self) -> Tuple[float, float]:
        """Calculate equity value from enterprise value."""
        net_debt = self.historical.get("net_debt", 0)
        shares_outstanding = self.historical.get("shares_outstanding", 1)

        self.equity_value_perpetuity = (
            self.enterprise_value_perpetuity - net_debt
        )
        self.equity_value_exit_multiple = (
            self.enterprise_value_exit_multiple - net_debt
        )

        self.value_per_share_perpetuity = safe_divide(
            self.equity_value_perpetuity, shares_outstanding
        )
        self.value_per_share_exit_multiple = safe_divide(
            self.equity_value_exit_multiple, shares_outstanding
        )

        return self.equity_value_perpetuity, self.equity_value_exit_multiple
