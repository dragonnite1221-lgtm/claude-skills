# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from churn_analyzer_base import *  # noqa: F403,E402


class RetentionAnalyzer:
    def __init__(self, customers, as_of=None):
        self.customers = customers
        self.as_of = as_of or date.today()

    def active_customers(self, as_of=None):
        as_of = as_of or self.as_of
        return [c for c in self.customers if c.is_active(as_of)]

    def churned_customers(self, start=None, end=None):
        """Customers who churned in [start, end]."""
        result = []
        for c in self.customers:
            if not c.churn_date:
                continue
            if start and c.churn_date < start:
                continue
            if end and c.churn_date > end:
                continue
            result.append(c)
        return result

    def arr_waterfall(self, period_start, period_end):
        """
        Calculate ARR waterfall for a given period.
        Returns dict with opening_arr, new_arr, expansion_arr, contraction_arr,
        churned_arr, closing_arr, nrr, grr.
        """
        # Opening: active at period start
        opening_customers = [c for c in self.customers if c.is_active(period_start)]
        opening_arr = sum(c.arr for c in opening_customers)
        opening_ids = {c.customer_id for c in opening_customers}

        # New: started during the period
        new_customers = [
            c for c in self.customers
            if period_start < c.start_date <= period_end
        ]
        new_arr = sum(c.arr for c in new_customers)

        # Churned: were active at start, churn_date within period
        churned = [
            c for c in opening_customers
            if c.churn_date and period_start < c.churn_date <= period_end
        ]
        churned_arr = sum(c.arr for c in churned)

        # Expansion and contraction: from customers active at opening
        expansion = sum(
            c.expansion_arr for c in opening_customers
            if not c.is_churned() or (c.churn_date and c.churn_date > period_end)
        )
        contraction = sum(
            c.contraction_arr for c in opening_customers
            if not c.is_churned() or (c.churn_date and c.churn_date > period_end)
        )

        closing_arr = opening_arr + new_arr + expansion - contraction - churned_arr

        grr = (opening_arr - contraction - churned_arr) / opening_arr if opening_arr else 0
        nrr = (opening_arr + expansion - contraction - churned_arr) / opening_arr if opening_arr else 0

        return {
            "period_start":   period_start.isoformat(),
            "period_end":     period_end.isoformat(),
            "opening_arr":    opening_arr,
            "new_arr":        new_arr,
            "expansion_arr":  expansion,
            "contraction_arr": contraction,
            "churned_arr":    churned_arr,
            "closing_arr":    closing_arr,
            "net_new_arr":    new_arr + expansion - contraction - churned_arr,
            "grr":            max(0.0, grr),
            "nrr":            max(0.0, nrr),
        }

    def logo_churn_rate(self, period_start, period_end):
        """Logo churn rate for a period."""
        opening = [c for c in self.customers if c.is_active(period_start)]
        churned = [
            c for c in opening
            if c.churn_date and period_start < c.churn_date <= period_end
        ]
        return len(churned) / len(opening) if opening else 0.0

    def revenue_churn_rate(self, period_start, period_end):
        """Gross revenue churn rate for a period."""
        opening = [c for c in self.customers if c.is_active(period_start)]
        opening_arr = sum(c.arr for c in opening)
        churned_arr = sum(
            c.arr for c in opening
            if c.churn_date and period_start < c.churn_date <= period_end
        )
        contraction = sum(c.contraction_arr for c in opening)
        return (churned_arr + contraction) / opening_arr if opening_arr else 0.0
