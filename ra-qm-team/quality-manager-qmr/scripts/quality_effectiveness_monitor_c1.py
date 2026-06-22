# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from quality_effectiveness_monitor_base import *  # noqa: F403,E402
from quality_effectiveness_monitor_p0 import QualityMetric  # noqa: F401,E501


class QMSEffectivenessMonitorMixin1:
    def detect_alerts(self, metrics: List[QualityMetric]) -> List[Dict]:
        """Detect metrics that require attention."""
        alerts = []
        for metric in metrics:
            # Check immediate control limit violation
            if metric.upper_limit and metric.value > metric.upper_limit:
                alerts.append({
                    "metric_id": metric.metric_id,
                    "metric_name": metric.metric_name,
                    "issue": "exceeds_upper_limit",
                    "value": metric.value,
                    "limit": metric.upper_limit,
                    "severity": "critical" if metric.category in ["Customer", "Regulatory"] else "high"
                })
            if metric.lower_limit and metric.value < metric.lower_limit:
                alerts.append({
                    "metric_id": metric.metric_id,
                    "metric_name": metric.metric_name,
                    "issue": "below_lower_limit",
                    "value": metric.value,
                    "limit": metric.lower_limit,
                    "severity": "critical" if metric.category in ["Customer", "Regulatory"] else "high"
                })

            # Check for adverse trend (3+ points in same direction)
            # Need to group by metric_name and check historical data
            # Simplified: check trend_direction flag if set
            if metric.trend_direction in ["up", "down"] and metric.sigma_level > 3:
                alerts.append({
                    "metric_id": metric.metric_id,
                    "metric_name": metric.metric_name,
                    "issue": f"adverse_trend_{metric.trend_direction}",
                    "value": metric.value,
                    "severity": "medium"
                })

        return alerts
    def predict_failures(self, metrics: List[QualityMetric], forecast_days: int = 30) -> List[Dict]:
        """Predict potential failures based on trends."""
        predictions = []

        # Group metrics by name to get time series
        grouped = {}
        for m in metrics:
            if m.metric_name not in grouped:
                grouped[m.metric_name] = []
            grouped[m.metric_name].append(m)

        for metric_name, metric_list in grouped.items():
            if len(metric_list) < 5:
                continue

            # Sort by date
            metric_list.sort(key=lambda m: m.date)
            values = [m.value for m in metric_list]

            # Simple linear extrapolation
            x = list(range(len(values)))
            y = values
            n = len(x)
            sum_x = sum(x)
            sum_y = sum(y)
            sum_xy = sum(x[i] * y[i] for i in range(n))
            sum_x2 = sum(xi * xi for xi in x)
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x) if (n * sum_x2 - sum_x * sum_x) != 0 else 0

            if slope != 0:
                # Forecast next value
                next_value = y[-1] + slope
                target = metric_list[0].target
                upper_limit = metric_list[0].upper_limit

                if (target and next_value > target * 1.2) or (upper_limit and next_value > upper_limit * 0.9):
                    predictions.append({
                        "metric": metric_name,
                        "current_value": y[-1],
                        "forecast_value": round(next_value, 2),
                        "forecast_days": forecast_days,
                        "trend_slope": round(slope, 3),
                        "risk_level": "high" if upper_limit and next_value > upper_limit else "medium"
                    })

        return predictions
    def calculate_effectiveness_score(self, metrics: List[QualityMetric]) -> float:
        """Calculate overall QMS effectiveness score (0-100)."""
        if not metrics:
            return 0.0

        scores = []
        for m in metrics:
            # Score based on distance to target
            if m.target != 0:
                deviation = abs(m.value - m.target) / max(abs(m.target), 1)
                score = max(0, 100 - deviation * 100)
            else:
                # For metrics where lower is better (defects, etc.)
                if m.upper_limit:
                    score = max(0, 100 - (m.value / m.upper_limit) * 100 * 0.5)
                else:
                    score = 50  # Neutral if no target
            scores.append(score)

        # Penalize for alerts
        alerts = self.detect_alerts(metrics)
        penalty = len([a for a in alerts if a["severity"] in ["critical", "high"]]) * 5
        return max(0, min(100, mean(scores) - penalty))
