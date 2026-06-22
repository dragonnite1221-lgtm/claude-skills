# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from budget_variance_analyzer_base import *  # noqa: F403,E402
from budget_variance_analyzer_p0 import safe_divide  # noqa: F401,E501


class BudgetVarianceAnalyzerMixin0:
    """Analyze budget variances with materiality filtering and classification."""
    def __init__(
        self,
        data: Dict[str, Any],
        threshold_pct: float = 10.0,
        threshold_amt: float = 50000.0,
    ) -> None:
        """
        Initialize the analyzer.

        Args:
            data: Budget data with line items
            threshold_pct: Materiality threshold as percentage (default 10%)
            threshold_amt: Materiality threshold as dollar amount (default $50K)
        """
        self.line_items: List[Dict[str, Any]] = data.get("line_items", [])
        self.period: str = data.get("period", "Current Period")
        self.company: str = data.get("company", "Company")
        self.threshold_pct = threshold_pct
        self.threshold_amt = threshold_amt
        self.variances: List[Dict[str, Any]] = []
        self.material_variances: List[Dict[str, Any]] = []
        self.summary: Dict[str, Any] = {}
    def classify_favorability(
        self, line_type: str, variance_amount: float
    ) -> str:
        """
        Classify variance as favorable or unfavorable.

        Revenue: over budget = favorable
        Expense: under budget = favorable
        """
        if line_type.lower() in ("revenue", "income", "sales"):
            return "Favorable" if variance_amount > 0 else "Unfavorable"
        else:
            # For expenses, under budget (negative variance) is favorable
            return "Favorable" if variance_amount < 0 else "Unfavorable"
    def calculate_variances(self) -> List[Dict[str, Any]]:
        """Calculate variances for all line items."""
        self.variances = []

        for item in self.line_items:
            name = item.get("name", "Unknown")
            line_type = item.get("type", "expense")
            department = item.get("department", "General")
            category = item.get("category", "Other")
            actual = item.get("actual", 0)
            budget = item.get("budget", 0)
            prior_year = item.get("prior_year", None)

            # Budget variance
            budget_var_amt = actual - budget
            budget_var_pct = safe_divide(budget_var_amt, budget) * 100

            # Prior year variance (if available)
            py_var_amt = (actual - prior_year) if prior_year is not None else None
            py_var_pct = (
                safe_divide(py_var_amt, prior_year) * 100
                if prior_year is not None
                else None
            )

            favorability = self.classify_favorability(line_type, budget_var_amt)

            is_material = (
                abs(budget_var_pct) >= self.threshold_pct
                or abs(budget_var_amt) >= self.threshold_amt
            )

            variance_record = {
                "name": name,
                "type": line_type,
                "department": department,
                "category": category,
                "actual": actual,
                "budget": budget,
                "prior_year": prior_year,
                "budget_variance_amount": budget_var_amt,
                "budget_variance_pct": round(budget_var_pct, 2),
                "prior_year_variance_amount": py_var_amt,
                "prior_year_variance_pct": (
                    round(py_var_pct, 2) if py_var_pct is not None else None
                ),
                "favorability": favorability,
                "is_material": is_material,
            }

            self.variances.append(variance_record)

        # Filter material variances
        self.material_variances = [v for v in self.variances if v["is_material"]]

        return self.variances
