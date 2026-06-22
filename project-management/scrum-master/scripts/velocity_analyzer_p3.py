# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from velocity_analyzer_base import *  # noqa: F403,E402
# fmt: off
from velocity_analyzer_p1 import FORECASTING_CONFIG, SprintData, VELOCITY_THRESHOLDS  # noqa: E402,E501
# fmt: on


def detect_anomalies(sprints: List[SprintData]) -> List[Dict[str, Any]]:
    """Detect velocity anomalies using statistical methods."""
    if len(sprints) < 3:
        return []
    
    velocities = [sprint.velocity for sprint in sprints]
    mean_velocity = statistics.mean(velocities)
    std_dev = statistics.stdev(velocities) if len(velocities) > 1 else 0
    
    anomalies = []
    threshold = VELOCITY_THRESHOLDS["anomaly_detection"]["outlier_threshold"]
    extreme_threshold = VELOCITY_THRESHOLDS["anomaly_detection"]["extreme_outlier"]
    
    for i, sprint in enumerate(sprints):
        if std_dev == 0:
            continue
            
        z_score = abs(sprint.velocity - mean_velocity) / std_dev
        
        if z_score >= extreme_threshold:
            anomaly_type = "extreme_outlier"
        elif z_score >= threshold:
            anomaly_type = "outlier"
        else:
            continue
        
        anomalies.append({
            "sprint_number": sprint.sprint_number,
            "sprint_name": sprint.sprint_name,
            "velocity": sprint.velocity,
            "expected_range": (mean_velocity - 2 * std_dev, mean_velocity + 2 * std_dev),
            "z_score": z_score,
            "anomaly_type": anomaly_type,
            "deviation_percentage": ((sprint.velocity - mean_velocity) / mean_velocity) * 100,
        })
    
    return anomalies
def random_normal(mean: float, std_dev: float) -> float:
    """Generate a random number from a normal distribution using Box-Muller transform."""
    import random
    import math
    
    # Box-Muller transformation
    u1 = random.random()
    u2 = random.random()
    
    z0 = math.sqrt(-2 * math.log(u1)) * math.cos(2 * math.pi * u2)
    return mean + z0 * std_dev
def monte_carlo_forecast(sprints: List[SprintData], sprints_ahead: int = 6) -> Dict[str, Any]:
    """Generate probabilistic velocity forecasts using Monte Carlo simulation."""
    if len(sprints) < FORECASTING_CONFIG["min_sprints_for_forecast"]:
        return {"error": "insufficient_historical_data"}
    
    # Use recent sprints for forecasting
    lookback = min(len(sprints), FORECASTING_CONFIG["max_sprints_lookback"])
    recent_sprints = sprints[-lookback:]
    velocities = [sprint.velocity for sprint in recent_sprints]
    
    if not velocities:
        return {"error": "no_velocity_data"}
    
    mean_velocity = statistics.mean(velocities)
    std_dev = statistics.stdev(velocities) if len(velocities) > 1 else 0
    
    # Monte Carlo simulation
    iterations = FORECASTING_CONFIG["monte_carlo_iterations"]
    confidence_levels = FORECASTING_CONFIG["confidence_levels"]
    
    simulated_totals = []
    
    for _ in range(iterations):
        total_points = 0
        for _ in range(sprints_ahead):
            # Sample from normal distribution
            if std_dev > 0:
                simulated_velocity = max(0, random_normal(mean_velocity, std_dev))
            else:
                simulated_velocity = mean_velocity
            total_points += simulated_velocity
        simulated_totals.append(total_points)
    
    # Calculate percentiles for confidence intervals
    simulated_totals.sort()
    forecasts = {}
    
    for confidence in confidence_levels:
        percentile_index = int(confidence * iterations)
        percentile_index = min(percentile_index, iterations - 1)
        forecasts[f"{int(confidence * 100)}%"] = simulated_totals[percentile_index]
    
    return {
        "sprints_ahead": sprints_ahead,
        "historical_sprints_used": lookback,
        "mean_velocity": mean_velocity,
        "velocity_std_dev": std_dev,
        "forecasted_totals": forecasts,
        "average_per_sprint": mean_velocity,
        "expected_total": mean_velocity * sprints_ahead,
    }
