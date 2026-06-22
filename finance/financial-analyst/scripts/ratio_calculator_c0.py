# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from ratio_calculator_base import *  # noqa: F403,E402
from ratio_calculator_p0 import safe_divide  # noqa: F401,E501


class FinancialRatioCalculatorMixin0:
    """Calculate and interpret financial ratios from statement data."""
    BENCHMARKS: Dict[str, Tuple[float, float, float]] = {
        "roe": (0.08, 0.15, 0.25),
        "roa": (0.03, 0.06, 0.12),
        "gross_margin": (0.25, 0.40, 0.60),
        "operating_margin": (0.05, 0.15, 0.25),
        "net_margin": (0.03, 0.10, 0.20),
        "current_ratio": (1.0, 1.5, 3.0),
        "quick_ratio": (0.8, 1.0, 2.0),
        "cash_ratio": (0.2, 0.5, 1.0),
        "debt_to_equity": (0.3, 0.8, 2.0),
        "interest_coverage": (2.0, 5.0, 10.0),
        "dscr": (1.0, 1.5, 2.5),
        "asset_turnover": (0.5, 1.0, 2.0),
        "inventory_turnover": (4.0, 8.0, 12.0),
        "receivables_turnover": (6.0, 10.0, 15.0),
        "dso": (30.0, 45.0, 60.0),
        "pe_ratio": (10.0, 20.0, 35.0),
        "pb_ratio": (1.0, 2.5, 5.0),
        "ps_ratio": (1.0, 3.0, 8.0),
        "ev_ebitda": (6.0, 12.0, 20.0),
        "peg_ratio": (0.5, 1.0, 2.0),
    }
    def __init__(self, data: Dict[str, Any]) -> None:
        """Initialize with financial statement data."""
        self.income = data.get("income_statement", {})
        self.balance = data.get("balance_sheet", {})
        self.cash_flow = data.get("cash_flow", {})
        self.market = data.get("market_data", {})
        self.results: Dict[str, Dict[str, Any]] = {}
    def calculate_profitability(self) -> Dict[str, Any]:
        """Calculate profitability ratios."""
        revenue = self.income.get("revenue", 0)
        cogs = self.income.get("cost_of_goods_sold", 0)
        operating_income = self.income.get("operating_income", 0)
        net_income = self.income.get("net_income", 0)
        total_equity = self.balance.get("total_equity", 0)
        total_assets = self.balance.get("total_assets", 0)

        gross_profit = revenue - cogs

        ratios = {
            "roe": {
                "value": safe_divide(net_income, total_equity),
                "formula": "Net Income / Total Equity",
                "name": "Return on Equity",
            },
            "roa": {
                "value": safe_divide(net_income, total_assets),
                "formula": "Net Income / Total Assets",
                "name": "Return on Assets",
            },
            "gross_margin": {
                "value": safe_divide(gross_profit, revenue),
                "formula": "(Revenue - COGS) / Revenue",
                "name": "Gross Margin",
            },
            "operating_margin": {
                "value": safe_divide(operating_income, revenue),
                "formula": "Operating Income / Revenue",
                "name": "Operating Margin",
            },
            "net_margin": {
                "value": safe_divide(net_income, revenue),
                "formula": "Net Income / Revenue",
                "name": "Net Margin",
            },
        }

        for key, ratio in ratios.items():
            ratio["interpretation"] = self.interpret_ratio(key, ratio["value"])

        self.results["profitability"] = ratios
        return ratios
    def calculate_liquidity(self) -> Dict[str, Any]:
        """Calculate liquidity ratios."""
        current_assets = self.balance.get("current_assets", 0)
        current_liabilities = self.balance.get("current_liabilities", 0)
        inventory = self.balance.get("inventory", 0)
        cash = self.balance.get("cash_and_equivalents", 0)

        ratios = {
            "current_ratio": {
                "value": safe_divide(current_assets, current_liabilities),
                "formula": "Current Assets / Current Liabilities",
                "name": "Current Ratio",
            },
            "quick_ratio": {
                "value": safe_divide(
                    current_assets - inventory, current_liabilities
                ),
                "formula": "(Current Assets - Inventory) / Current Liabilities",
                "name": "Quick Ratio",
            },
            "cash_ratio": {
                "value": safe_divide(cash, current_liabilities),
                "formula": "Cash & Equivalents / Current Liabilities",
                "name": "Cash Ratio",
            },
        }

        for key, ratio in ratios.items():
            ratio["interpretation"] = self.interpret_ratio(key, ratio["value"])

        self.results["liquidity"] = ratios
        return ratios
