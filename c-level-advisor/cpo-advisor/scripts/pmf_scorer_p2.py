# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from pmf_scorer_base import *  # noqa: F403,E402
# fmt: off
from pmf_scorer_p1 import clamp, cohort_trend, score_between  # noqa: E402,E501
# fmt: on


def score_retention(data: dict, thresholds: dict) -> tuple[float, list]:
    """Returns (score 0-1, list of findings)."""
    r = data.get("retention", {})
    findings = []
    scores = []

    d30 = r.get("d30_cohorts", [])
    d90 = r.get("d90_cohorts", [])

    if not d30:
        findings.append("⚠ No D30 retention data — this is the most important PMF signal. Instrument it immediately.")
        return 0.0, findings

    latest_d30 = d30[0]
    d30_score = score_between(latest_d30, 0, thresholds["d30_strong"])
    scores.append(d30_score)

    if latest_d30 >= thresholds["d30_strong"]:
        findings.append(f"✓ D30 retention {latest_d30:.0%} — strong PMF signal")
    elif latest_d30 >= thresholds["d30_pmf"]:
        findings.append(f"◑ D30 retention {latest_d30:.0%} — approaching PMF threshold ({thresholds['d30_pmf']:.0%})")
    else:
        findings.append(f"✗ D30 retention {latest_d30:.0%} — below PMF threshold ({thresholds['d30_pmf']:.0%}). Focus here before anything else.")

    # Trend bonus
    if len(d30) >= 2:
        trend = cohort_trend(d30)
        trend_score = (trend + 1) / 2  # normalize to 0-1
        scores.append(trend_score * 0.5)  # trend is bonus, not primary
        if trend > 0.1:
            findings.append(f"✓ D30 retention improving across cohorts — strong learning signal")
        elif trend < -0.1:
            findings.append(f"✗ D30 retention declining across cohorts — product changes may be hurting core users")

    if d90:
        latest_d90 = d90[0]
        d90_score = score_between(latest_d90, 0, thresholds["d90_strong"])
        scores.append(d90_score)
        if latest_d90 >= thresholds["d90_strong"]:
            findings.append(f"✓ D90 retention {latest_d90:.0%} — excellent long-term retention")
        elif latest_d90 >= thresholds["d90_pmf"]:
            findings.append(f"◑ D90 retention {latest_d90:.0%} — some long-term value demonstrated")
        else:
            findings.append(f"✗ D90 retention {latest_d90:.0%} — users not finding long-term value")
    else:
        findings.append("⚠ No D90 data. Add 90-day cohort tracking.")

    flattening = r.get("curve_flattening", False)
    if flattening:
        scores.append(0.8)
        findings.append("✓ Retention curve flattening — core retained segment exists")
    else:
        scores.append(0.2)
        findings.append("✗ Retention curve not flattening — no stable retained segment yet")

    return clamp(sum(scores) / len(scores)), findings
def score_engagement(data: dict, thresholds: dict) -> tuple[float, list]:
    e = data.get("engagement", {})
    findings = []
    scores = []

    dau_mau = e.get("dau_mau_ratio")
    if dau_mau is not None:
        s = score_between(dau_mau, 0, thresholds["dau_mau_strong"])
        scores.append(s)
        if dau_mau >= thresholds["dau_mau_strong"]:
            findings.append(f"✓ DAU/MAU {dau_mau:.0%} — strong daily habit")
        elif dau_mau >= thresholds["dau_mau_pmf"]:
            findings.append(f"◑ DAU/MAU {dau_mau:.0%} — moderate engagement")
        else:
            findings.append(f"✗ DAU/MAU {dau_mau:.0%} — users not building a habit. Find the daily job or accept weekly use pattern.")
    else:
        findings.append("⚠ No DAU/MAU data.")

    sessions = e.get("avg_sessions_per_week")
    if sessions is not None:
        # 5+ sessions/week = strong, 2 = threshold
        s = score_between(sessions, 1, 5)
        scores.append(s)
        if sessions >= 5:
            findings.append(f"✓ {sessions:.1f} sessions/week — high engagement")
        elif sessions >= 2:
            findings.append(f"◑ {sessions:.1f} sessions/week — moderate")
        else:
            findings.append(f"✗ {sessions:.1f} sessions/week — very low. Users not returning within week.")
    else:
        findings.append("⚠ No session frequency data.")

    kar = e.get("key_action_rate")
    if kar is not None:
        s = score_between(kar, 0.10, 0.70)
        scores.append(s)
        if kar >= 0.60:
            findings.append(f"✓ Key action rate {kar:.0%} — core value well-adopted")
        elif kar >= 0.30:
            findings.append(f"◑ Key action rate {kar:.0%} — improve onboarding to drive this up")
        else:
            findings.append(f"✗ Key action rate {kar:.0%} — most users not reaching core value. This is an activation problem.")
    else:
        findings.append("⚠ No key action rate. Define your 'aha moment' action and track it.")

    depth = e.get("session_depth_score")
    if depth is not None:
        scores.append(depth)
        if depth >= 0.6:
            findings.append(f"✓ Session depth {depth:.1f} — users exploring the product")
        else:
            findings.append(f"◑ Session depth {depth:.1f} — users sticking to narrow feature set")

    if not scores:
        return 0.0, findings
    return clamp(sum(scores) / len(scores)), findings
