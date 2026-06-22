# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from budget_variance_analyzer_base import *  # noqa: F403,E402
from budget_variance_analyzer_p0 import safe_divide  # noqa: F401,E501


class BudgetVarianceAnalyzerMixin2:
    def generate_executive_summary(self) -> Dict[str, Any]:
        """Generate an executive summary of the variance analysis."""
        total_actual = sum(
            v["actual"] for v in self.variances if v["type"].lower() in ("revenue", "income", "sales")
        )
        total_budget = sum(
            v["budget"] for v in self.variances if v["type"].lower() in ("revenue", "income", "sales")
        )
        total_expense_actual = sum(
            v["actual"] for v in self.variances if v["type"].lower() not in ("revenue", "income", "sales")
        )
        total_expense_budget = sum(
            v["budget"] for v in self.variances if v["type"].lower() not in ("revenue", "income", "sales")
        )

        revenue_variance = total_actual - total_budget
        expense_variance = total_expense_actual - total_expense_budget

        favorable_count = sum(
            1 for v in self.variances if v["favorability"] == "Favorable"
        )
        unfavorable_count = sum(
            1 for v in self.variances if v["favorability"] == "Unfavorable"
        )

        self.summary = {
            "period": self.period,
            "company": self.company,
            "total_line_items": len(self.variances),
            "material_variances_count": len(self.material_variances),
            "favorable_count": favorable_count,
            "unfavorable_count": unfavorable_count,
            "revenue": {
                "actual": total_actual,
                "budget": total_budget,
                "variance_amount": revenue_variance,
                "variance_pct": round(
                    safe_divide(revenue_variance, total_budget) * 100, 2
                ),
            },
            "expenses": {
                "actual": total_expense_actual,
                "budget": total_expense_budget,
                "variance_amount": expense_variance,
                "variance_pct": round(
                    safe_divide(expense_variance, total_expense_budget) * 100, 2
                ),
            },
            "net_impact": revenue_variance - expense_variance,
            "materiality_thresholds": {
                "percentage": self.threshold_pct,
                "amount": self.threshold_amt,
            },
        }

        return self.summary
    def run_analysis(self) -> Dict[str, Any]:
        """Run the complete variance analysis."""
        self.calculate_variances()
        dept_summary = self.department_summary()
        cat_summary = self.category_summary()
        exec_summary = self.generate_executive_summary()

        return {
            "executive_summary": exec_summary,
            "all_variances": self.variances,
            "material_variances": self.material_variances,
            "department_summary": dept_summary,
            "category_summary": cat_summary,
        }
