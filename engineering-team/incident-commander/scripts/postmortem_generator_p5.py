# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from postmortem_generator_base import *  # noqa: F403,E402
# fmt: off
from postmortem_generator_p1 import BENCHMARKS, POSTMORTEM_TARGET_HOURS  # noqa: E402,E501
from postmortem_generator_p4 import PostmortemReport  # noqa: E402,E501
# fmt: on


def _generate_lessons(report: PostmortemReport) -> List[str]:
    """Derive lessons learned from the analysis."""
    lessons: List[str] = []
    bench = BENCHMARKS.get(report.incident.severity, BENCHMARKS["SEV3"])
    mttd = report.timeline.mttd
    if mttd is not None and mttd > bench["mttd"]:
        lessons.append(
            f"Detection took {mttd:.0f} minutes, exceeding the {bench['mttd']}-minute "
            f"benchmark for {report.incident.severity}. Invest in earlier detection mechanisms.")
    dist = report.factor_distribution
    dominant = max(dist, key=lambda k: dist[k])
    if dist[dominant] >= 50:
        lessons.append(
            f"The '{dominant}' category accounts for {dist[dominant]:.0f}% of contributing factors. "
            f"Targeted improvements in this area will yield the highest return.")
    if report.coverage_gaps:
        lessons.append(
            f"There are {len(report.coverage_gaps)} action item coverage gap(s). "
            "Ensure every contributing factor category has a corresponding remediation action.")
    avg_q = (sum(a.quality_score for a in report.action_items) / len(report.action_items)
             if report.action_items else 0)
    if avg_q < 70:
        lessons.append(
            f"Average action item quality score is {avg_q:.0f}/100. "
            "Make action items more specific with measurable targets and clear ownership.")
    if report.timeline.postmortem_on_time is False:
        h = report.timeline.postmortem_timeliness_hours
        lessons.append(
            f"Postmortem was held {h:.0f} hours after resolution, exceeding the "
            f"{POSTMORTEM_TARGET_HOURS}-hour target. Schedule postmortems sooner to capture context.")
    if not lessons:
        lessons.append("This incident was handled within benchmarks. Continue reinforcing "
                       "current practices and share this postmortem for organizational learning.")
    return lessons
