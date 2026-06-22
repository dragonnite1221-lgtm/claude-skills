# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from quality_effectiveness_monitor_base import *  # noqa: F403,E402
from quality_effectiveness_monitor_p0 import QualityMetric  # noqa: F401,E501


class QMSEffectivenessMonitorMixin0:
    """Monitors and analyzes QMS effectiveness."""
    SIGNAL_INDICATORS = {
        "complaint_rate": {"unit": "per 1000 units", "target": 0, "upper_limit": 1.5},
        "defect_rate": {"unit": "PPM", "target": 100, "upper_limit": 500},
        "rework_rate": {"unit": "%", "target": 2.0, "upper_limit": 5.0},
        "on_time_delivery": {"unit": "%", "target": 98, "lower_limit": 95},
        "audit_findings": {"unit": "count/month", "target": 0, "upper_limit": 3},
        "capa_closure_rate": {"unit": "% within target", "target": 100, "lower_limit": 90},
        "supplier_defect_rate": {"unit": "PPM", "target": 200, "upper_limit": 1000}
    }
    def __init__(self):
        self.metrics = []
    def load_csv(self, csv_path: str) -> List[QualityMetric]:
        """Load metrics from CSV file."""
        metrics = []
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                metric = QualityMetric(
                    metric_id=row.get('metric_id', ''),
                    metric_name=row.get('metric_name', ''),
                    category=row.get('category', 'General'),
                    date=row.get('date', ''),
                    value=float(row.get('value', 0)),
                    unit=row.get('unit', ''),
                    target=float(row.get('target', 0)),
                    upper_limit=float(row.get('upper_limit', 0)),
                    lower_limit=float(row.get('lower_limit', 0)),
                )
                metrics.append(metric)
        self.metrics = metrics
        return metrics
    def calculate_sigma_level(self, metric: QualityMetric, historical_values: List[float]) -> float:
        """Calculate process sigma level based on defect rate."""
        if metric.unit == "PPM" or "rate" in metric.metric_name.lower():
            # For defect rates, DPMO = defects_per_million_opportunities
            if historical_values:
                avg_defect_rate = mean(historical_values)
                if avg_defect_rate > 0:
                    dpmo = avg_defect_rate
                    # Simplified sigma conversion (actual uses 1.5σ shift)
                    sigma_map = {
                        330000: 1.0, 620000: 2.0, 110000: 3.0, 27000: 4.0,
                        6200: 5.0, 230: 6.0, 3.4: 6.0
                    }
                    # Rough sigma calculation
                    sigma = 6.0 - (dpmo / 1000000) * 10
                    return max(0.0, min(6.0, sigma))
        return 0.0
    def analyze_trend(self, values: List[float]) -> Tuple[str, float]:
        """Analyze trend direction and significance."""
        if len(values) < 3:
            return "insufficient_data", 0.0

        x = list(range(len(values)))
        y = values

        # Linear regression
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(xi * xi for xi in x)

        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x) if (n * sum_x2 - sum_x * sum_x) != 0 else 0

        # Determine trend direction
        if slope > 0.01:
            direction = "up"
        elif slope < -0.01:
            direction = "down"
        else:
            direction = "stable"

        # Calculate R-squared
        if slope != 0:
            intercept = (sum_y - slope * sum_x) / n
            y_pred = [slope * xi + intercept for xi in x]
            ss_res = sum((y[i] - y_pred[i])**2 for i in range(n))
            ss_tot = sum((y[i] - mean(y))**2 for i in range(n))
            r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        else:
            r2 = 0

        return direction, r2
