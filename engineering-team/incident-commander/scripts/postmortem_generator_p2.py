# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from postmortem_generator_base import *  # noqa: F403,E402
# fmt: off
from postmortem_generator_p1 import BENCHMARKS, CAT_TO_ACTION, CAT_WEIGHT, FACTOR_KEYWORDS, POSTMORTEM_TARGET_HOURS, WHY_TEMPLATES  # noqa: E402,E501
# fmt: on


class TimelineMetrics:
    """MTTD, MTTR, and other timing metrics computed from raw timestamps."""
    def __init__(self, timeline: Dict[str, str], severity: str) -> None:
        self.severity = severity
        self.issue_started = self._parse(timeline.get("issue_started"))
        self.detected_at = self._parse(timeline.get("detected_at"))
        self.declared_at = self._parse(timeline.get("declared_at"))
        self.mitigated_at = self._parse(timeline.get("mitigated_at"))
        self.resolved_at = self._parse(timeline.get("resolved_at"))
        self.postmortem_at = self._parse(timeline.get("postmortem_at"))

    @staticmethod
    def _parse(ts: Optional[str]) -> Optional[datetime]:
        if ts is None:
            return None
        for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S"):
            try:
                dt = datetime.strptime(ts, fmt)
                return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
            except ValueError:
                continue
        return None

    def _delta_min(self, start: Optional[datetime], end: Optional[datetime]) -> Optional[float]:
        if start is None or end is None:
            return None
        return round((end - start).total_seconds() / 60.0, 1)

    @property
    def mttd(self) -> Optional[float]:
        return self._delta_min(self.issue_started, self.detected_at)

    @property
    def mttr(self) -> Optional[float]:
        return self._delta_min(self.detected_at, self.resolved_at)

    @property
    def time_to_mitigate(self) -> Optional[float]:
        return self._delta_min(self.detected_at, self.mitigated_at)

    @property
    def time_to_declare(self) -> Optional[float]:
        return self._delta_min(self.detected_at, self.declared_at)

    @property
    def postmortem_timeliness_hours(self) -> Optional[float]:
        m = self._delta_min(self.resolved_at, self.postmortem_at)
        return round(m / 60.0, 1) if m is not None else None

    @property
    def postmortem_on_time(self) -> Optional[bool]:
        h = self.postmortem_timeliness_hours
        return h <= POSTMORTEM_TARGET_HOURS if h is not None else None

    def benchmark_comparison(self) -> Dict[str, Dict[str, Any]]:
        bench = BENCHMARKS.get(self.severity, BENCHMARKS["SEV3"])
        results: Dict[str, Dict[str, Any]] = {}
        for name, actual, target in [("mttd", self.mttd, bench["mttd"]),
                                     ("mttr", self.mttr, bench["mttr"]),
                                     ("time_to_mitigate", self.time_to_mitigate, bench["mitigate"]),
                                     ("time_to_declare", self.time_to_declare, bench["declare"])]:
            if actual is not None:
                results[name] = {"actual_minutes": actual, "benchmark_minutes": target,
                                 "met_benchmark": actual <= target,
                                 "delta_minutes": round(actual - target, 1)}
        h = self.postmortem_timeliness_hours
        if h is not None:
            results["postmortem_timeliness"] = {
                "actual_hours": h, "target_hours": POSTMORTEM_TARGET_HOURS,
                "met_target": self.postmortem_on_time, "delta_hours": round(h - POSTMORTEM_TARGET_HOURS, 1)}
        return results

    def to_dict(self) -> Dict[str, Any]:
        return {"mttd_minutes": self.mttd, "mttr_minutes": self.mttr,
                "time_to_mitigate_minutes": self.time_to_mitigate,
                "time_to_declare_minutes": self.time_to_declare,
                "postmortem_timeliness_hours": self.postmortem_timeliness_hours,
                "postmortem_on_time": self.postmortem_on_time,
                "benchmarks": self.benchmark_comparison()}
class ContributingFactor:
    """A classified contributing factor with weight and action-type mapping."""
    def __init__(self, description: str, index: int) -> None:
        self.description = description
        self.index = index
        self.category = self._classify()
        self.weight = round(max(1.0 - index * 0.15, 0.3) * CAT_WEIGHT.get(self.category, 0.8), 2)
        self.mapped_action_type = CAT_TO_ACTION.get(self.category, "process")

    def _classify(self) -> str:
        lower = self.description.lower()
        scores = {cat: sum(1 for kw in kws if kw in lower) for cat, kws in FACTOR_KEYWORDS.items()}
        best = max(scores, key=lambda k: scores[k])
        return best if scores[best] > 0 else "process"

    def to_dict(self) -> Dict[str, Any]:
        return {"description": self.description, "category": self.category,
                "weight": self.weight, "mapped_action_type": self.mapped_action_type}
class FiveWhysAnalysis:
    """Structured 5-Whys chain for a contributing factor."""
    def __init__(self, factor: ContributingFactor) -> None:
        self.factor = factor
        self.systemic_theme: str = factor.category
        self.chain: List[str] = [f"Why? {factor.description}"] + \
            WHY_TEMPLATES.get(factor.category, WHY_TEMPLATES["process"])

    def to_dict(self) -> Dict[str, Any]:
        return {"factor": self.factor.description, "category": self.factor.category,
                "chain": self.chain, "systemic_theme": self.systemic_theme}
