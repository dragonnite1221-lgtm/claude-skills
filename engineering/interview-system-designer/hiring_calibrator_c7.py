# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from hiring_calibrator_base import *  # noqa: F403,E402


class HiringCalibratorMixin7:
    def _analyze_trends_over_time(self, data: List[Dict[str, Any]], period: str) -> Dict[str, Any]:
        """Analyze trends in hiring patterns over time."""
        
        # Sort data by date
        dated_data = [record for record in data if record.get("date")]
        dated_data.sort(key=lambda x: x["date"])
        
        if len(dated_data) < 10:  # Need minimum data for trend analysis
            return {"error": "Insufficient data for trend analysis", "minimum_required": 10}
        
        # Group by time period
        period_groups = defaultdict(list)
        
        for record in dated_data:
            date = record["date"]
            
            if period == "weekly":
                period_key = date.strftime("%Y-W%U")
            elif period == "monthly":
                period_key = date.strftime("%Y-%m")
            elif period == "quarterly":
                quarter = (date.month - 1) // 3 + 1
                period_key = f"{date.year}-Q{quarter}"
            else:  # daily
                period_key = date.strftime("%Y-%m-%d")
            
            period_groups[period_key].append(record)
        
        # Calculate metrics for each period
        period_metrics = {}
        for period_key, records in period_groups.items():
            if len(records) >= 3:  # Minimum for meaningful metrics
                scores = [r["average_score"] for r in records]
                hire_rate = sum(r["hire_decision"] for r in records) / len(records)
                
                period_metrics[period_key] = {
                    "count": len(records),
                    "mean_score": statistics.mean(scores),
                    "hire_rate": hire_rate,
                    "std_score": statistics.stdev(scores) if len(scores) > 1 else 0
                }
        
        if len(period_metrics) < 3:
            return {"error": "Insufficient periods for trend analysis"}
        
        # Analyze trends
        sorted_periods = sorted(period_metrics.keys())
        mean_scores = [period_metrics[p]["mean_score"] for p in sorted_periods]
        hire_rates = [period_metrics[p]["hire_rate"] for p in sorted_periods]
        
        # Simple linear trend calculation
        score_trend = self._calculate_linear_trend(mean_scores)
        hire_rate_trend = self._calculate_linear_trend(hire_rates)
        
        return {
            "period": period,
            "total_periods": len(period_metrics),
            "period_metrics": period_metrics,
            "trends": {
                "score_trend": {
                    "direction": "increasing" if score_trend > 0.01 else "decreasing" if score_trend < -0.01 else "stable",
                    "slope": round(score_trend, 4),
                    "significance": "significant" if abs(score_trend) > 0.05 else "minor"
                },
                "hire_rate_trend": {
                    "direction": "increasing" if hire_rate_trend > 0.005 else "decreasing" if hire_rate_trend < -0.005 else "stable",
                    "slope": round(hire_rate_trend, 4),
                    "significance": "significant" if abs(hire_rate_trend) > 0.02 else "minor"
                }
            },
            "insights": self._generate_trend_insights(score_trend, hire_rate_trend, period_metrics)
        }
    def _calculate_linear_trend(self, values: List[float]) -> float:
        """Calculate simple linear trend slope."""
        if len(values) < 2:
            return 0
        
        n = len(values)
        x = list(range(n))
        
        # Calculate slope using least squares
        x_mean = statistics.mean(x)
        y_mean = statistics.mean(values)
        
        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        return numerator / denominator if denominator != 0 else 0
