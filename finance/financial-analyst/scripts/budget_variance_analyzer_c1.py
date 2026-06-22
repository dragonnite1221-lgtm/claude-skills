# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from budget_variance_analyzer_base import *  # noqa: F403,E402
from budget_variance_analyzer_p0 import safe_divide  # noqa: F401,E501


class BudgetVarianceAnalyzerMixin1:
    def department_summary(self) -> Dict[str, Dict[str, Any]]:
        """Summarize variances by department."""
        departments: Dict[str, Dict[str, float]] = {}

        for v in self.variances:
            dept = v["department"]
            if dept not in departments:
                departments[dept] = {
                    "total_actual": 0.0,
                    "total_budget": 0.0,
                    "total_variance": 0.0,
                    "favorable_count": 0,
                    "unfavorable_count": 0,
                    "line_count": 0,
                }

            departments[dept]["total_actual"] += v["actual"]
            departments[dept]["total_budget"] += v["budget"]
            departments[dept]["total_variance"] += v["budget_variance_amount"]
            departments[dept]["line_count"] += 1
            if v["favorability"] == "Favorable":
                departments[dept]["favorable_count"] += 1
            else:
                departments[dept]["unfavorable_count"] += 1

        # Add variance percentage
        for dept_data in departments.values():
            dept_data["variance_pct"] = round(
                safe_divide(
                    dept_data["total_variance"], dept_data["total_budget"]
                )
                * 100,
                2,
            )

        return departments
    def category_summary(self) -> Dict[str, Dict[str, Any]]:
        """Summarize variances by category."""
        categories: Dict[str, Dict[str, float]] = {}

        for v in self.variances:
            cat = v["category"]
            if cat not in categories:
                categories[cat] = {
                    "total_actual": 0.0,
                    "total_budget": 0.0,
                    "total_variance": 0.0,
                    "line_count": 0,
                }

            categories[cat]["total_actual"] += v["actual"]
            categories[cat]["total_budget"] += v["budget"]
            categories[cat]["total_variance"] += v["budget_variance_amount"]
            categories[cat]["line_count"] += 1

        for cat_data in categories.values():
            cat_data["variance_pct"] = round(
                safe_divide(
                    cat_data["total_variance"], cat_data["total_budget"]
                )
                * 100,
                2,
            )

        return categories
