# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from dcf_valuation_base import *  # noqa: F403,E402


class DCFModelMixin0:
    """Discounted Cash Flow valuation model."""
    def __init__(self) -> None:
        """Initialize the DCF model."""
        self.historical: Dict[str, Any] = {}
        self.assumptions: Dict[str, Any] = {}
        self.wacc: float = 0.0
        self.projected_revenue: List[float] = []
        self.projected_fcf: List[float] = []
        self.projection_years: int = 5
        self.terminal_value_perpetuity: float = 0.0
        self.terminal_value_exit_multiple: float = 0.0
        self.enterprise_value_perpetuity: float = 0.0
        self.enterprise_value_exit_multiple: float = 0.0
        self.equity_value_perpetuity: float = 0.0
        self.equity_value_exit_multiple: float = 0.0
        self.value_per_share_perpetuity: float = 0.0
        self.value_per_share_exit_multiple: float = 0.0
    def set_historical_financials(self, historical: Dict[str, Any]) -> None:
        """Set historical financial data."""
        self.historical = historical
    def set_assumptions(self, assumptions: Dict[str, Any]) -> None:
        """Set projection assumptions."""
        self.assumptions = assumptions
        self.projection_years = assumptions.get("projection_years", 5)
    def calculate_wacc(self) -> float:
        """Calculate Weighted Average Cost of Capital via CAPM."""
        wacc_inputs = self.assumptions.get("wacc_inputs", {})

        risk_free_rate = wacc_inputs.get("risk_free_rate", 0.04)
        equity_risk_premium = wacc_inputs.get("equity_risk_premium", 0.06)
        beta = wacc_inputs.get("beta", 1.0)
        cost_of_debt = wacc_inputs.get("cost_of_debt", 0.05)
        tax_rate = wacc_inputs.get("tax_rate", 0.25)
        debt_weight = wacc_inputs.get("debt_weight", 0.30)
        equity_weight = wacc_inputs.get("equity_weight", 0.70)

        # CAPM: Cost of Equity = Risk-Free Rate + Beta * Equity Risk Premium
        cost_of_equity = risk_free_rate + beta * equity_risk_premium

        # WACC = (E/V * Re) + (D/V * Rd * (1 - T))
        after_tax_cost_of_debt = cost_of_debt * (1 - tax_rate)
        self.wacc = (equity_weight * cost_of_equity) + (
            debt_weight * after_tax_cost_of_debt
        )

        return self.wacc
    def project_cash_flows(self) -> Tuple[List[float], List[float]]:
        """Project revenue and free cash flow over the projection period."""
        base_revenue = self.historical.get("revenue", [])
        if not base_revenue:
            raise ValueError("Historical revenue data is required")

        last_revenue = base_revenue[-1]

        revenue_growth_rates = self.assumptions.get("revenue_growth_rates", [])
        fcf_margins = self.assumptions.get("fcf_margins", [])

        # If growth rates not provided for all years, use average or default
        default_growth = self.assumptions.get("default_revenue_growth", 0.05)
        default_fcf_margin = self.assumptions.get("default_fcf_margin", 0.10)

        self.projected_revenue = []
        self.projected_fcf = []
        current_revenue = last_revenue

        for year in range(self.projection_years):
            growth = (
                revenue_growth_rates[year]
                if year < len(revenue_growth_rates)
                else default_growth
            )
            fcf_margin = (
                fcf_margins[year]
                if year < len(fcf_margins)
                else default_fcf_margin
            )

            current_revenue = current_revenue * (1 + growth)
            fcf = current_revenue * fcf_margin

            self.projected_revenue.append(current_revenue)
            self.projected_fcf.append(fcf)

        return self.projected_revenue, self.projected_fcf
    def calculate_terminal_value(self) -> Tuple[float, float]:
        """Calculate terminal value using both perpetuity growth and exit multiple."""
        if not self.projected_fcf:
            raise ValueError("Must project cash flows before terminal value")

        terminal_fcf = self.projected_fcf[-1]
        terminal_growth = self.assumptions.get("terminal_growth_rate", 0.025)
        exit_multiple = self.assumptions.get("exit_ev_ebitda_multiple", 12.0)

        # Perpetuity growth method: TV = FCF * (1+g) / (WACC - g)
        if self.wacc > terminal_growth:
            self.terminal_value_perpetuity = (
                terminal_fcf * (1 + terminal_growth)
            ) / (self.wacc - terminal_growth)
        else:
            self.terminal_value_perpetuity = 0.0

        # Exit multiple method: TV = Terminal EBITDA * Exit Multiple
        terminal_revenue = self.projected_revenue[-1]
        ebitda_margin = self.assumptions.get("terminal_ebitda_margin", 0.20)
        terminal_ebitda = terminal_revenue * ebitda_margin
        self.terminal_value_exit_multiple = terminal_ebitda * exit_multiple

        return self.terminal_value_perpetuity, self.terminal_value_exit_multiple
