# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from forecast_builder_base import *  # noqa: F403,E402
from forecast_builder_p0 import simple_linear_regression  # noqa: F401,E501


class ForecastBuilderMixin0:
    """Driver-based revenue forecasting with scenario modeling."""
    def __init__(self, data: Dict[str, Any]) -> None:
        """Initialize the forecast builder."""
        self.historical: List[Dict[str, Any]] = data.get("historical_periods", [])
        self.drivers: Dict[str, Any] = data.get("drivers", {})
        self.assumptions: Dict[str, Any] = data.get("assumptions", {})
        self.cash_flow_inputs: Dict[str, Any] = data.get("cash_flow_inputs", {})
        self.scenarios_config: Dict[str, Any] = data.get("scenarios", {})
        self.forecast_periods: int = data.get("forecast_periods", 12)
    def analyze_trends(self) -> Dict[str, Any]:
        """Analyze historical trends using linear regression."""
        if not self.historical:
            return {"error": "No historical data available"}

        # Extract revenue series
        revenues = [p.get("revenue", 0) for p in self.historical]
        periods = list(range(1, len(revenues) + 1))

        slope, intercept, r_squared = simple_linear_regression(
            [float(x) for x in periods],
            [float(y) for y in revenues],
        )

        # Calculate growth rates
        growth_rates = []
        for i in range(1, len(revenues)):
            if revenues[i - 1] > 0:
                growth = (revenues[i] - revenues[i - 1]) / revenues[i - 1]
                growth_rates.append(growth)

        avg_growth = mean(growth_rates) if growth_rates else 0.0

        # Seasonality detection (if enough data)
        seasonality_index: List[float] = []
        if len(revenues) >= 4:
            overall_avg = mean(revenues)
            if overall_avg > 0:
                seasonality_index = [r / overall_avg for r in revenues[-4:]]

        return {
            "trend": {
                "slope": round(slope, 2),
                "intercept": round(intercept, 2),
                "r_squared": round(r_squared, 4),
                "direction": "upward" if slope > 0 else "downward" if slope < 0 else "flat",
            },
            "growth_rates": [round(g, 4) for g in growth_rates],
            "average_growth_rate": round(avg_growth, 4),
            "seasonality_index": [round(s, 4) for s in seasonality_index],
            "historical_revenues": revenues,
        }
