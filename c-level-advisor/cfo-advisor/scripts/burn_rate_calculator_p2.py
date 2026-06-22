# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from burn_rate_calculator_base import *  # noqa: F403,E402
# fmt: off
from burn_rate_calculator_p1 import HiringEntry, ModelConfig, MonthResult  # noqa: E402,E501
# fmt: on


class RunwayCalculator:

    def __init__(self, config: ModelConfig):
        self.cfg = config

    def run(self) -> list[MonthResult]:
        cfg = self.cfg
        results = []

        # Build headcount schedule: month -> list of new hires starting that month
        hire_by_month: dict[int, list[HiringEntry]] = {}
        for h in cfg.hiring_plan:
            hire_by_month.setdefault(h.month, []).append(h)

        # Track existing employees
        active_employees: list[dict] = []
        for _ in range(cfg.starting_headcount):
            active_employees.append({
                "monthly_loaded": cfg.avg_loaded_salary / 12 * 1.0,
                "start_month": 0,
            })

        cash = cfg.starting_cash
        mrr = cfg.starting_mrr
        cumulative_new_arr = 0.0
        starting_mrr = cfg.starting_mrr

        for m in range(1, cfg.model_months + 1):
            # Process new hires this month
            one_time_recruiting = 0.0
            if m in hire_by_month:
                for hire in hire_by_month[m]:
                    monthly_loaded = (
                        hire.annual_salary * (1 + hire.benefits_pct) / 12
                    )
                    active_employees.append({
                        "monthly_loaded": monthly_loaded,
                        "start_month": m,
                    })
                    one_time_recruiting += hire.recruiting_cost

            # Revenue this month
            mrr = mrr * (1 + cfg.mrr_growth_rate)
            gross_profit = mrr * cfg.gross_margin_pct

            # Headcount cost
            headcount_cost = sum(e["monthly_loaded"] for e in active_employees)
            headcount_cost += one_time_recruiting

            # Other opex (infra, SaaS tools, office, etc.)
            other_opex = cfg.base_non_headcount_opex

            # Burn
            gross_burn = headcount_cost + other_opex
            net_burn = gross_burn - gross_profit

            # Cash
            cash_start = cash
            cash = cash - net_burn
            cash_end = cash

            # Projected runway from this month (using current net burn rate)
            runway = cash_end / net_burn if net_burn > 0 else float("inf")

            # Cumulative new ARR (for burn multiple calc)
            new_mrr_added = mrr - starting_mrr if m == 1 else mrr - results[-1].mrr
            cumulative_new_arr += new_mrr_added * 12

            # Label
            if cfg.start_date:
                month_date = date(
                    cfg.start_date.year,
                    cfg.start_date.month,
                    1,
                ) + timedelta(days=32 * (m - 1))
                month_date = month_date.replace(day=1)
                label = f"Month {m:02d} ({month_date.strftime('%b %Y')})"
            else:
                label = f"Month {m:02d}"

            results.append(MonthResult(
                month=m,
                label=label,
                mrr=mrr,
                gross_profit=gross_profit,
                headcount=len(active_employees),
                headcount_cost=headcount_cost,
                other_opex=other_opex,
                gross_burn=gross_burn,
                net_burn=net_burn,
                cash_start=cash_start,
                cash_end=cash_end,
                runway_months=runway,
                cumulative_new_arr=cumulative_new_arr,
            ))

            # Stop if cash runs out
            if cash_end <= 0:
                break

        return results

    def cash_out_date(self, results: list[MonthResult]) -> Optional[str]:
        """Return the label of the month cash runs out, or None if model survives."""
        for r in results:
            if r.cash_end <= 0:
                return r.label
        return None

    def burn_multiple(self, results: list[MonthResult]) -> float:
        """Burn multiple = total net burn / total net new ARR over model period."""
        total_net_burn = sum(r.net_burn for r in results if r.net_burn > 0)
        first_mrr = results[0].mrr / (1 + self.cfg.mrr_growth_rate)  # starting mrr
        total_new_arr = (results[-1].mrr - first_mrr) * 12
        if total_new_arr <= 0:
            return float("inf")
        return total_net_burn / total_new_arr
def fmt_k(value: float) -> str:
    """Format as $Xk or $X.XM."""
    if abs(value) >= 1_000_000:
        return f"${value/1_000_000:.2f}M"
    if abs(value) >= 1_000:
        return f"${value/1_000:.0f}K"
    return f"${value:.0f}"
