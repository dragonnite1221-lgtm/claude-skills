# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from revenue_forecast_model_base import *  # noqa: F403,E402
# fmt: off
from revenue_forecast_model_p1 import DEFAULT_STAGE_PROBABILITIES, SCENARIO_MULTIPLIERS  # noqa: E402,E501
# fmt: on


class ForecastEngine:
    def __init__(self, deals, stage_probs=None):
        self.deals = deals
        self.stage_probs = stage_probs or DEFAULT_STAGE_PROBABILITIES

    def open_deals(self):
        return [d for d in self.deals if d.is_open()]

    def closed_won_deals(self):
        return [d for d in self.deals if d.is_closed_won()]

    def pipeline_by_month(self, scenario="base"):
        """Returns dict: month_key → weighted ARR."""
        result = defaultdict(float)
        for deal in self.open_deals():
            result[deal.month_key] += deal.weighted_value(self.stage_probs, scenario)
        return dict(sorted(result.items()))

    def pipeline_by_quarter(self, scenario="base"):
        """Returns dict: quarter → weighted ARR."""
        result = defaultdict(float)
        for deal in self.open_deals():
            result[deal.quarter] += deal.weighted_value(self.stage_probs, scenario)
        return dict(sorted(result.items()))

    def coverage_ratio(self, quota, period_filter=None):
        """
        Pipeline coverage = total pipeline ÷ quota.
        period_filter: if set, only include deals with close_date in that period.
        """
        pipeline = sum(
            d.arr_value for d in self.open_deals()
            if period_filter is None or d.quarter == period_filter
        )
        return pipeline / quota if quota else 0.0

    def scenario_summary(self, periods=None):
        """
        Returns dict: period → {conservative, base, upside, open_pipeline}.
        periods: list of month_keys to include; if None, all months.
        """
        summaries = {}
        all_months = sorted(set(d.month_key for d in self.open_deals()))
        target_months = periods or all_months

        for month in target_months:
            deals_in_month = [d for d in self.open_deals() if d.month_key == month]
            if not deals_in_month:
                continue
            summaries[month] = {
                "deal_count":    len(deals_in_month),
                "open_pipeline": sum(d.arr_value for d in deals_in_month),
                "conservative":  sum(d.weighted_value(self.stage_probs, "conservative") for d in deals_in_month),
                "base":          sum(d.weighted_value(self.stage_probs, "base") for d in deals_in_month),
                "upside":        sum(d.weighted_value(self.stage_probs, "upside") for d in deals_in_month),
            }
        return summaries

    def rep_performance(self):
        """Returns dict: rep → {pipeline, weighted_base, deal_count, avg_deal_size}."""
        rep_data = defaultdict(lambda: {"pipeline": 0.0, "weighted_base": 0.0,
                                        "deal_count": 0, "deals": []})
        for deal in self.open_deals():
            rep_data[deal.rep]["pipeline"] += deal.arr_value
            rep_data[deal.rep]["weighted_base"] += deal.weighted_value(self.stage_probs, "base")
            rep_data[deal.rep]["deal_count"] += 1
            rep_data[deal.rep]["deals"].append(deal.arr_value)

        result = {}
        for rep, data in rep_data.items():
            deals = data["deals"]
            result[rep] = {
                "pipeline":      data["pipeline"],
                "weighted_base": data["weighted_base"],
                "deal_count":    data["deal_count"],
                "avg_deal_size": statistics.mean(deals) if deals else 0.0,
            }
        return result

    def segment_breakdown(self, scenario="base"):
        """Returns dict: segment → weighted ARR."""
        result = defaultdict(float)
        for deal in self.open_deals():
            result[deal.segment or "unspecified"] += deal.weighted_value(self.stage_probs, scenario)
        return dict(result)

    def stage_distribution(self):
        """Returns dict: stage → {count, total_arr, avg_arr}."""
        result = defaultdict(lambda: {"count": 0, "total_arr": 0.0})
        for deal in self.open_deals():
            result[deal.stage]["count"] += 1
            result[deal.stage]["total_arr"] += deal.arr_value
        out = {}
        for stage, data in result.items():
            out[stage] = {
                "count":     data["count"],
                "total_arr": data["total_arr"],
                "avg_arr":   data["total_arr"] / data["count"] if data["count"] else 0,
                "probability": self.stage_probs.get(stage, 0.0),
            }
        return out

    def confidence_interval(self, scenario="base", iterations=1000):
        """
        Monte Carlo simulation to generate confidence interval around base forecast.
        Each deal wins/loses based on its probability; runs iterations times.
        Returns (p10, p50, p90) of total expected ARR.
        """
        import random
        random.seed(42)

        totals = []
        for _ in range(iterations):
            total = 0.0
            for deal in self.open_deals():
                prob = min(1.0, self.stage_probs.get(deal.stage, 0.0) * SCENARIO_MULTIPLIERS[scenario])
                if random.random() < prob:
                    total += deal.arr_value
            totals.append(total)

        totals.sort()
        n = len(totals)
        return (
            totals[int(n * 0.10)],  # P10 (conservative)
            totals[int(n * 0.50)],  # P50 (median)
            totals[int(n * 0.90)],  # P90 (upside)
        )
