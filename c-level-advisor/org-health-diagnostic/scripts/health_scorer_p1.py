# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from health_scorer_base import *  # noqa: F403,E402


class Stage(Enum):
    SEED = "seed"
    SERIES_A = "series_a"
    SERIES_B = "series_b"
    SERIES_C = "series_c"
class Trend(Enum):
    IMPROVING = "improving"
    STABLE = "stable"
    DECLINING = "declining"
    UNKNOWN = "unknown"
class TrafficLight(Enum):
    GREEN = "green"
    YELLOW = "yellow"
    RED = "red"
STAGE_WEIGHTS = {
    Stage.SEED: {
        "financial": 0.30, "revenue": 0.20, "people": 0.20,
        "product": 0.15, "engineering": 0.10, "operations": 0.05,
        "market": 0.00, "security": 0.00
    },
    Stage.SERIES_A: {
        "financial": 0.25, "revenue": 0.25, "people": 0.15,
        "product": 0.15, "engineering": 0.10, "operations": 0.05,
        "market": 0.05, "security": 0.00
    },
    Stage.SERIES_B: {
        "financial": 0.20, "revenue": 0.25, "people": 0.15,
        "product": 0.15, "engineering": 0.10, "operations": 0.08,
        "market": 0.05, "security": 0.02
    },
    Stage.SERIES_C: {
        "financial": 0.20, "revenue": 0.25, "people": 0.15,
        "product": 0.15, "engineering": 0.10, "operations": 0.08,
        "market": 0.05, "security": 0.02
    },
}
@dataclass
class Metric:
    name: str
    value: Optional[float]
    unit: str
    green_threshold: float    # value at or above this = green
    red_threshold: float      # value at or below this = red
    higher_is_better: bool = True

    def score(self) -> Optional[float]:
        """Score 1-10. Returns None if no value."""
        if self.value is None:
            return None
        v = self.value
        g = self.green_threshold
        r = self.red_threshold

        if self.higher_is_better:
            if v >= g:
                # Scale 7-10 based on how far above green
                excess = min((v - g) / max(g * 0.3, 0.01), 1.0)
                return 7.0 + (3.0 * excess)
            elif v <= r:
                # Scale 1-3 based on how far below red
                deficit = min((r - v) / max(r * 0.5, 0.01), 1.0)
                return max(1.0, 3.0 - (2.0 * deficit))
            else:
                # Between red and green → 4-6
                if g == r:
                    return 5.0
                position = (v - r) / (g - r)
                return 4.0 + (2.0 * position)
        else:
            # Lower is better — invert
            if v <= g:
                excess = min((g - v) / max(g * 0.3, 0.01), 1.0)
                return 7.0 + (3.0 * excess)
            elif v >= r:
                deficit = min((v - r) / max(r * 0.5, 0.01), 1.0)
                return max(1.0, 3.0 - (2.0 * deficit))
            else:
                if g == r:
                    return 5.0
                position = (r - v) / (r - g)
                return 4.0 + (2.0 * position)

    def traffic_light(self) -> Optional[TrafficLight]:
        s = self.score()
        if s is None:
            return None
        if s >= 7:
            return TrafficLight.GREEN
        elif s >= 4:
            return TrafficLight.YELLOW
        return TrafficLight.RED
@dataclass
class Dimension:
    key: str
    name: str
    owner: str
    emoji: str
    metrics: List[Metric]
    trend: Trend = Trend.UNKNOWN
    notes: str = ""

    def score(self) -> Optional[float]:
        """Average of available metric scores."""
        scores = [m.score() for m in self.metrics if m.score() is not None]
        if not scores:
            return None
        return round(sum(scores) / len(scores), 1)

    def traffic_light(self) -> TrafficLight:
        s = self.score()
        if s is None:
            return TrafficLight.YELLOW  # Unknown = watch
        if s >= 7:
            return TrafficLight.GREEN
        elif s >= 4:
            return TrafficLight.YELLOW
        return TrafficLight.RED

    def coverage(self) -> float:
        """% of metrics with data."""
        filled = sum(1 for m in self.metrics if m.value is not None)
        return filled / len(self.metrics) if self.metrics else 0.0

    def missing_metrics(self) -> List[str]:
        return [m.name for m in self.metrics if m.value is None]
