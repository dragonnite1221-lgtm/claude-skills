# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from revenue_forecast_model_base import *  # noqa: F403,E402


DEFAULT_STAGE_PROBABILITIES = {
    "discovery":     0.10,
    "qualification": 0.25,
    "demo":          0.40,
    "proposal":      0.55,
    "poc":           0.65,
    "negotiation":   0.80,
    "verbal_commit": 0.92,
    "closed_won":    1.00,
    "closed_lost":   0.00,
}
SCENARIO_MULTIPLIERS = {
    "conservative": 0.85,  # Win rate 15% below historical
    "base":         1.00,  # Historical win rate
    "upside":       1.15,  # Win rate 15% above historical
}
class Deal:
    def __init__(self, deal_id, name, stage, arr_value, close_date, rep="", segment=""):
        self.deal_id = deal_id
        self.name = name
        self.stage = stage.lower().replace(" ", "_").replace("/", "_")
        self.arr_value = float(arr_value)
        self.close_date = self._parse_date(close_date)
        self.rep = rep
        self.segment = segment

    @staticmethod
    def _parse_date(value):
        for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d"):
            try:
                return datetime.strptime(str(value), fmt).date()
            except ValueError:
                continue
        raise ValueError(f"Cannot parse date: {value!r}")

    @property
    def quarter(self):
        q = (self.close_date.month - 1) // 3 + 1
        return f"Q{q} {self.close_date.year}"

    @property
    def month_key(self):
        return self.close_date.strftime("%Y-%m")

    def weighted_value(self, stage_probs, scenario="base"):
        prob = stage_probs.get(self.stage, 0.0)
        multiplier = SCENARIO_MULTIPLIERS.get(scenario, 1.0)
        # Clamp probability to [0, 1]
        adjusted = min(1.0, max(0.0, prob * multiplier))
        return self.arr_value * adjusted

    def is_open(self):
        return self.stage not in ("closed_won", "closed_lost")

    def is_closed_won(self):
        return self.stage == "closed_won"
def calculate_historical_win_rates(deals):
    """
    Calculate actual win rates per stage from closed deals.
    Returns a dict: stage → win_rate (float).
    Requires deals that were at each stage and are now closed won/lost.
    """
    # In a real implementation, you'd have historical stage-at-point-in-time data.
    # Here we approximate: among closed deals, what fraction were won?
    closed = [d for d in deals if not d.is_open()]
    if not closed:
        return {}

    won = [d for d in closed if d.is_closed_won()]
    overall_rate = len(won) / len(closed) if closed else 0.0

    # Stage-level calibration: adjust default probs by actual overall rate
    # (In production: use CRM historical stage-level conversion data)
    calibrated = {}
    for stage, default_prob in DEFAULT_STAGE_PROBABILITIES.items():
        if overall_rate > 0:
            calibrated[stage] = min(1.0, default_prob * (overall_rate / 0.25))
        else:
            calibrated[stage] = default_prob

    return calibrated
