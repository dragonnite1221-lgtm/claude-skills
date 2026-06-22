# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from ratio_calculator_base import *  # noqa: F403,E402
from ratio_calculator_p0 import safe_divide  # noqa: F401,E501


class FinancialRatioCalculatorMixin1:
    def calculate_leverage(self) -> Dict[str, Any]:
        """Calculate leverage ratios."""
        total_debt = self.balance.get("total_debt", 0)
        total_equity = self.balance.get("total_equity", 0)
        operating_income = self.income.get("operating_income", 0)
        interest_expense = self.income.get("interest_expense", 0)
        operating_cash_flow = self.cash_flow.get("operating_cash_flow", 0)
        total_debt_service = self.cash_flow.get(
            "total_debt_service", interest_expense
        )

        ratios = {
            "debt_to_equity": {
                "value": safe_divide(total_debt, total_equity),
                "formula": "Total Debt / Total Equity",
                "name": "Debt-to-Equity Ratio",
            },
            "interest_coverage": {
                "value": safe_divide(operating_income, interest_expense),
                "formula": "Operating Income / Interest Expense",
                "name": "Interest Coverage Ratio",
            },
            "dscr": {
                "value": safe_divide(operating_cash_flow, total_debt_service),
                "formula": "Operating Cash Flow / Total Debt Service",
                "name": "Debt Service Coverage Ratio",
            },
        }

        for key, ratio in ratios.items():
            ratio["interpretation"] = self.interpret_ratio(key, ratio["value"])

        self.results["leverage"] = ratios
        return ratios
    def calculate_efficiency(self) -> Dict[str, Any]:
        """Calculate efficiency ratios."""
        revenue = self.income.get("revenue", 0)
        cogs = self.income.get("cost_of_goods_sold", 0)
        total_assets = self.balance.get("total_assets", 0)
        inventory = self.balance.get("inventory", 0)
        accounts_receivable = self.balance.get("accounts_receivable", 0)

        receivables_turnover_val = safe_divide(revenue, accounts_receivable)

        ratios = {
            "asset_turnover": {
                "value": safe_divide(revenue, total_assets),
                "formula": "Revenue / Total Assets",
                "name": "Asset Turnover",
            },
            "inventory_turnover": {
                "value": safe_divide(cogs, inventory),
                "formula": "COGS / Inventory",
                "name": "Inventory Turnover",
            },
            "receivables_turnover": {
                "value": receivables_turnover_val,
                "formula": "Revenue / Accounts Receivable",
                "name": "Receivables Turnover",
            },
            "dso": {
                "value": safe_divide(365, receivables_turnover_val)
                if receivables_turnover_val > 0
                else 0.0,
                "formula": "365 / Receivables Turnover",
                "name": "Days Sales Outstanding",
            },
        }

        for key, ratio in ratios.items():
            ratio["interpretation"] = self.interpret_ratio(key, ratio["value"])

        self.results["efficiency"] = ratios
        return ratios
