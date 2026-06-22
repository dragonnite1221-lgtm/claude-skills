# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from ratio_calculator_base import *  # noqa: F403,E402
from ratio_calculator_p0 import safe_divide  # noqa: F401,E501


class FinancialRatioCalculatorMixin2:
    def calculate_valuation(self) -> Dict[str, Any]:
        """Calculate valuation ratios (requires market data)."""
        market_cap = self.market.get("market_cap", 0)
        share_price = self.market.get("share_price", 0)
        shares_outstanding = self.market.get("shares_outstanding", 0)
        earnings_growth_rate = self.market.get("earnings_growth_rate", 0)

        net_income = self.income.get("net_income", 0)
        revenue = self.income.get("revenue", 0)
        total_equity = self.balance.get("total_equity", 0)
        total_debt = self.balance.get("total_debt", 0)
        cash = self.balance.get("cash_and_equivalents", 0)
        ebitda = self.income.get("ebitda", 0)

        if market_cap == 0 and share_price > 0 and shares_outstanding > 0:
            market_cap = share_price * shares_outstanding

        eps = safe_divide(net_income, shares_outstanding)
        book_value_per_share = safe_divide(total_equity, shares_outstanding)
        enterprise_value = market_cap + total_debt - cash
        pe = safe_divide(share_price, eps)

        ratios = {
            "pe_ratio": {
                "value": pe,
                "formula": "Share Price / Earnings Per Share",
                "name": "Price-to-Earnings Ratio",
            },
            "pb_ratio": {
                "value": safe_divide(share_price, book_value_per_share),
                "formula": "Share Price / Book Value Per Share",
                "name": "Price-to-Book Ratio",
            },
            "ps_ratio": {
                "value": safe_divide(
                    market_cap, revenue
                ),
                "formula": "Market Cap / Revenue",
                "name": "Price-to-Sales Ratio",
            },
            "ev_ebitda": {
                "value": safe_divide(enterprise_value, ebitda),
                "formula": "Enterprise Value / EBITDA",
                "name": "EV/EBITDA",
            },
            "peg_ratio": {
                "value": safe_divide(pe, earnings_growth_rate * 100)
                if earnings_growth_rate > 0
                else 0.0,
                "formula": "P/E Ratio / Earnings Growth Rate (%)",
                "name": "PEG Ratio",
            },
        }

        for key, ratio in ratios.items():
            ratio["interpretation"] = self.interpret_ratio(key, ratio["value"])

        self.results["valuation"] = ratios
        return ratios
    def calculate_all(self) -> Dict[str, Dict[str, Any]]:
        """Calculate all ratio categories."""
        self.calculate_profitability()
        self.calculate_liquidity()
        self.calculate_leverage()
        self.calculate_efficiency()
        self.calculate_valuation()
        return self.results
    def interpret_ratio(self, ratio_key: str, value: float) -> str:
        """Interpret a ratio value against benchmarks."""
        if value == 0.0:
            return "Insufficient data to calculate"

        benchmarks = self.BENCHMARKS.get(ratio_key)
        if not benchmarks:
            return "No benchmark available"

        low, typical, high = benchmarks

        # DSO is inverse - lower is better
        if ratio_key == "dso":
            if value <= low:
                return "Excellent - collections well above average"
            elif value <= typical:
                return "Good - collections within normal range"
            elif value <= high:
                return "Acceptable - monitor collection trends"
            else:
                return "Concern - collections significantly slower than peers"

        # Debt-to-equity - lower generally better (but context matters)
        if ratio_key == "debt_to_equity":
            if value <= low:
                return "Conservative leverage - strong equity position"
            elif value <= typical:
                return "Moderate leverage - well balanced"
            elif value <= high:
                return "Elevated leverage - monitor debt levels"
            else:
                return "High leverage - potential financial risk"

        # Standard interpretation (higher is better for most ratios)
        if value < low:
            return "Below average - needs improvement"
        elif value <= typical:
            return "Acceptable - within normal range"
        elif value <= high:
            return "Good - above average performance"
        else:
            return "Excellent - significantly above peers"
