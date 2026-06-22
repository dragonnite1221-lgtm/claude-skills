# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from debt_dashboard_base import *  # noqa: F403,E402
from debt_dashboard_p0 import TrendAnalysis  # noqa: F401,E501


class DebtDashboardMixin4:
    def _calculate_trend(self, values: List[float], dates: List[datetime], metric_name: str) -> TrendAnalysis:
        """Calculate trend analysis for a specific metric."""
        if len(values) < 2:
            return TrendAnalysis(metric_name, "stable", 0.0, 0.0, values[-1], (values[-1], values[-1]))
        
        # Calculate simple linear trend
        n = len(values)
        x = list(range(n))  # Time periods as numbers
        
        # Linear regression
        x_mean = mean(x)
        y_mean = mean(values)
        
        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            slope = 0
        else:
            slope = numerator / denominator
        
        # Correlation strength
        if n > 2 and len(set(values)) > 1:
            try:
                correlation = numerator / (
                    (sum((x[i] - x_mean) ** 2 for i in range(n)) * 
                     sum((values[i] - y_mean) ** 2 for i in range(n))) ** 0.5
                )
            except ZeroDivisionError:
                correlation = 0.0
        else:
            correlation = 0.0
        
        # Determine trend direction
        if abs(slope) < 0.1:
            trend_direction = "stable"
        elif slope > 0:
            if metric_name in ["overall_score", "quality_score"]:
                trend_direction = "improving"  # Higher is better
            else:
                trend_direction = "declining"  # Higher is worse
        else:
            if metric_name in ["overall_score", "quality_score"]:
                trend_direction = "declining"
            else:
                trend_direction = "improving"
        
        # Forecast next period
        forecast = values[-1] + slope
        
        # Confidence interval (simple approach)
        if n > 2:
            residuals = [values[i] - (y_mean + slope * (x[i] - x_mean)) for i in range(n)]
            std_error = (sum(r**2 for r in residuals) / (n - 2)) ** 0.5
            confidence_interval = (forecast - std_error, forecast + std_error)
        else:
            confidence_interval = (forecast, forecast)
        
        return TrendAnalysis(
            metric_name=metric_name,
            trend_direction=trend_direction,
            change_rate=round(slope, 3),
            correlation_strength=round(correlation, 3),
            forecast_next_period=round(forecast, 2),
            confidence_interval=(round(confidence_interval[0], 2), round(confidence_interval[1], 2))
        )
