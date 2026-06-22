# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from velocity_analyzer_base import *  # noqa: F403,E402
# fmt: off
from velocity_analyzer_p1 import SprintData, VELOCITY_THRESHOLDS  # noqa: E402,E501
# fmt: on


def detect_trend(sprints: List[SprintData], lookback_sprints: int = 6) -> Dict[str, Any]:
    """Detect velocity trends using linear regression and statistical analysis."""
    if len(sprints) < 3:
        return {"trend": "insufficient_data", "confidence": 0.0}
    
    # Use recent sprints for trend analysis
    recent_sprints = sprints[-lookback_sprints:] if len(sprints) > lookback_sprints else sprints
    velocities = [sprint.velocity for sprint in recent_sprints]
    
    # Calculate linear trend
    n = len(velocities)
    x_values = list(range(n))
    x_mean = sum(x_values) / n
    y_mean = sum(velocities) / n
    
    # Linear regression slope
    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, velocities))
    denominator = sum((x - x_mean) ** 2 for x in x_values)
    
    if denominator == 0:
        slope = 0
    else:
        slope = numerator / denominator
    
    # Calculate correlation coefficient for trend strength
    if n > 2:
        try:
            correlation = statistics.correlation(x_values, velocities)
        except statistics.StatisticsError:
            correlation = 0.0
    else:
        correlation = 0.0
    
    # Determine trend direction and strength
    avg_velocity = statistics.mean(velocities)
    relative_slope = slope / max(avg_velocity, 1)  # Normalize by average velocity
    
    thresholds = VELOCITY_THRESHOLDS["trend_detection"]
    
    if relative_slope > thresholds["strong_improvement"]:
        trend = "strong_improvement"
    elif relative_slope > thresholds["improvement"]:
        trend = "improvement"
    elif relative_slope > -thresholds["stable"]:
        trend = "stable"
    elif relative_slope > thresholds["decline"]:
        trend = "decline"
    else:
        trend = "strong_decline"
    
    return {
        "trend": trend,
        "slope": slope,
        "relative_slope": relative_slope,
        "correlation": abs(correlation),
        "confidence": abs(correlation),
        "recent_sprints_analyzed": len(recent_sprints),
        "average_velocity": avg_velocity,
    }
def calculate_volatility(sprints: List[SprintData]) -> Dict[str, Any]:
    """Calculate velocity volatility and stability metrics."""
    if len(sprints) < 2:
        return {"volatility": "insufficient_data"}
    
    velocities = [sprint.velocity for sprint in sprints]
    mean_velocity = statistics.mean(velocities)
    
    if mean_velocity == 0:
        return {"volatility": "no_velocity"}
    
    # Coefficient of Variation (CV)
    std_dev = statistics.stdev(velocities) if len(velocities) > 1 else 0
    cv = std_dev / mean_velocity
    
    # Classify volatility
    thresholds = VELOCITY_THRESHOLDS["volatility"]
    
    if cv <= thresholds["low"]:
        volatility_level = "low"
    elif cv <= thresholds["moderate"]:
        volatility_level = "moderate"
    elif cv <= thresholds["high"]:
        volatility_level = "high"
    else:
        volatility_level = "very_high"
    
    # Calculate additional stability metrics
    velocity_range = max(velocities) - min(velocities)
    range_ratio = velocity_range / mean_velocity if mean_velocity > 0 else 0
    
    return {
        "volatility": volatility_level,
        "coefficient_of_variation": cv,
        "standard_deviation": std_dev,
        "mean_velocity": mean_velocity,
        "velocity_range": velocity_range,
        "range_ratio": range_ratio,
        "min_velocity": min(velocities),
        "max_velocity": max(velocities),
    }
