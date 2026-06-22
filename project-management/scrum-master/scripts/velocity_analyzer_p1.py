# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from velocity_analyzer_base import *  # noqa: F403,E402


VELOCITY_THRESHOLDS: Dict[str, Dict[str, float]] = {
    "trend_detection": {
        "strong_improvement": 0.15,    # 15% improvement
        "improvement": 0.08,           # 8% improvement
        "stable": 0.05,                # ±5% stable range
        "decline": -0.08,              # 8% decline
        "strong_decline": -0.15,       # 15% decline
    },
    "volatility": {
        "low": 0.15,                   # CV below 15%
        "moderate": 0.25,              # CV 15-25%
        "high": 0.40,                  # CV 25-40%
        "very_high": 0.40,             # CV above 40%
    },
    "anomaly_detection": {
        "outlier_threshold": 2.0,      # Standard deviations from mean
        "extreme_outlier": 3.0,        # Extreme outlier threshold
    }
}
FORECASTING_CONFIG: Dict[str, Any] = {
    "confidence_levels": [0.50, 0.70, 0.85, 0.95],
    "monte_carlo_iterations": 10000,
    "min_sprints_for_forecast": 3,
    "max_sprints_lookback": 8,
}
class SprintData:
    """Represents a single sprint's velocity and metadata."""
    
    def __init__(self, data: Dict[str, Any]):
        self.sprint_number: int = data.get("sprint_number", 0)
        self.sprint_name: str = data.get("sprint_name", "")
        self.start_date: str = data.get("start_date", "")
        self.end_date: str = data.get("end_date", "")
        self.planned_points: int = data.get("planned_points", 0)
        self.completed_points: int = data.get("completed_points", 0)
        self.added_points: int = data.get("added_points", 0)
        self.removed_points: int = data.get("removed_points", 0)
        self.carry_over_points: int = data.get("carry_over_points", 0)
        self.team_capacity: float = data.get("team_capacity", 0.0)
        self.working_days: int = data.get("working_days", 10)
        
        # Calculate derived metrics
        self.velocity: int = self.completed_points
        self.commitment_ratio: float = (
            self.completed_points / max(self.planned_points, 1)
        )
        self.scope_change_ratio: float = (
            (self.added_points + self.removed_points) / max(self.planned_points, 1)
        )
class VelocityAnalysis:
    """Complete velocity analysis results."""
    
    def __init__(self):
        self.summary: Dict[str, Any] = {}
        self.trend_analysis: Dict[str, Any] = {}
        self.forecasting: Dict[str, Any] = {}
        self.anomalies: List[Dict[str, Any]] = []
        self.recommendations: List[str] = []
def calculate_rolling_averages(sprints: List[SprintData], 
                             window_sizes: List[int] = [3, 5, 8]) -> Dict[int, List[float]]:
    """Calculate rolling averages for different window sizes."""
    velocities = [sprint.velocity for sprint in sprints]
    rolling_averages = {}
    
    for window_size in window_sizes:
        averages = []
        for i in range(len(velocities)):
            start_idx = max(0, i - window_size + 1)
            window = velocities[start_idx:i + 1]
            if len(window) >= min(3, window_size):  # Minimum data points
                averages.append(sum(window) / len(window))
            else:
                averages.append(None)
        rolling_averages[window_size] = averages
    
    return rolling_averages
