# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from forecast_builder_base import *  # noqa: F403,E402
from forecast_builder_p0 import safe_divide  # noqa: F401,E501


class ForecastBuilderMixin2:
    def build_rolling_cash_flow(self, weeks: int = 13) -> Dict[str, Any]:
        """Build a 13-week rolling cash flow projection."""
        cfi = self.cash_flow_inputs

        opening_balance = cfi.get("opening_cash_balance", 0)
        weekly_revenue = cfi.get("weekly_revenue", 0)
        collection_rate = cfi.get("collection_rate", 0.85)
        collection_lag_weeks = cfi.get("collection_lag_weeks", 2)

        # Weekly expenses
        weekly_payroll = cfi.get("weekly_payroll", 0)
        weekly_rent = cfi.get("weekly_rent", 0)
        weekly_operating = cfi.get("weekly_operating", 0)
        weekly_other = cfi.get("weekly_other", 0)
        total_weekly_expenses = weekly_payroll + weekly_rent + weekly_operating + weekly_other

        # One-time items
        one_time_items: List[Dict[str, Any]] = cfi.get("one_time_items", [])

        weekly_projections: List[Dict[str, Any]] = []
        running_balance = opening_balance

        # Revenue pipeline for lagged collections
        revenue_pipeline: List[float] = [0.0] * collection_lag_weeks

        for week in range(1, weeks + 1):
            # Revenue collections (lagged)
            revenue_pipeline.append(weekly_revenue)
            collections = revenue_pipeline.pop(0) * collection_rate

            # One-time items for this week
            one_time_inflows = 0.0
            one_time_outflows = 0.0
            one_time_labels: List[str] = []
            for item in one_time_items:
                if item.get("week") == week:
                    amount = item.get("amount", 0)
                    if amount > 0:
                        one_time_inflows += amount
                    else:
                        one_time_outflows += abs(amount)
                    one_time_labels.append(item.get("description", ""))

            total_inflows = collections + one_time_inflows
            total_outflows = total_weekly_expenses + one_time_outflows
            net_cash_flow = total_inflows - total_outflows
            running_balance += net_cash_flow

            weekly_projections.append({
                "week": week,
                "collections": round(collections, 2),
                "one_time_inflows": round(one_time_inflows, 2),
                "total_inflows": round(total_inflows, 2),
                "payroll": round(weekly_payroll, 2),
                "rent": round(weekly_rent, 2),
                "operating": round(weekly_operating, 2),
                "other_expenses": round(weekly_other, 2),
                "one_time_outflows": round(one_time_outflows, 2),
                "total_outflows": round(total_outflows, 2),
                "net_cash_flow": round(net_cash_flow, 2),
                "closing_balance": round(running_balance, 2),
                "notes": ", ".join(one_time_labels) if one_time_labels else "",
            })

        # Summary
        total_inflows = sum(w["total_inflows"] for w in weekly_projections)
        total_outflows = sum(w["total_outflows"] for w in weekly_projections)
        min_balance = min(w["closing_balance"] for w in weekly_projections)
        min_balance_week = next(
            w["week"]
            for w in weekly_projections
            if w["closing_balance"] == min_balance
        )

        return {
            "weeks": weeks,
            "opening_balance": opening_balance,
            "closing_balance": round(running_balance, 2),
            "total_inflows": round(total_inflows, 2),
            "total_outflows": round(total_outflows, 2),
            "net_change": round(total_inflows - total_outflows, 2),
            "minimum_balance": round(min_balance, 2),
            "minimum_balance_week": min_balance_week,
            "cash_runway_weeks": (
                round(safe_divide(running_balance, total_weekly_expenses))
                if total_weekly_expenses > 0
                else None
            ),
            "weekly_projections": weekly_projections,
        }
