# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from pmf_scorer_base import *  # noqa: F403,E402
# fmt: off
from pmf_scorer_p1 import clamp, score_between  # noqa: E402,E501
# fmt: on


def score_satisfaction(data: dict, thresholds: dict) -> tuple[float, list]:
    s_data = data.get("satisfaction", {})
    findings = []
    scores = []

    se_score = s_data.get("sean_ellis_very_disappointed")
    se_n = s_data.get("sean_ellis_sample_size", 0)
    if se_score is not None:
        if se_n < 40:
            findings.append(f"⚠ Sean Ellis n={se_n} — too small to be reliable. Need 40+ responses.")
            scores.append(score_between(se_score, 0, thresholds["sean_ellis_strong"]) * 0.5)  # half weight
        else:
            s = score_between(se_score, 0, thresholds["sean_ellis_strong"])
            scores.append(s)
            if se_score >= thresholds["sean_ellis_strong"]:
                findings.append(f"✓ Sean Ellis {se_score:.0%} 'very disappointed' — strong PMF signal (n={se_n})")
            elif se_score >= thresholds["sean_ellis_pmf"]:
                findings.append(f"◑ Sean Ellis {se_score:.0%} — at PMF threshold. Push to > {thresholds['sean_ellis_strong']:.0%}.")
            else:
                findings.append(f"✗ Sean Ellis {se_score:.0%} — below {thresholds['sean_ellis_pmf']:.0%} threshold. Interview 'somewhat disappointed' group.")
    else:
        findings.append("⚠ No Sean Ellis data. Run a one-question survey to your active users now.")

    nps = s_data.get("nps_score")
    nps_n = s_data.get("nps_sample_size", 0)
    if nps is not None:
        if nps_n < 50:
            findings.append(f"⚠ NPS n={nps_n} — sample too small. Need 50+ for reliability.")
        # NPS ranges from -100 to 100; normalize to 0-1 against threshold
        s = score_between(nps, -20, thresholds["nps_strong"])
        scores.append(s)
        if nps >= thresholds["nps_strong"]:
            findings.append(f"✓ NPS {nps} — excellent. Promoters will drive organic growth.")
        elif nps >= thresholds["nps_pmf"]:
            findings.append(f"◑ NPS {nps} — acceptable. Focus on converting passives to promoters.")
        elif nps >= 0:
            findings.append(f"✗ NPS {nps} — low. More detractors than promoters is a warning sign.")
        else:
            findings.append(f"✗ NPS {nps} — negative. Active detractors outnumber promoters.")
    else:
        findings.append("⚠ No NPS data.")

    if not scores:
        return 0.0, findings
    return clamp(sum(scores) / len(scores)), findings
def score_growth(data: dict, _thresholds: dict) -> tuple[float, list]:
    g = data.get("growth", {})
    findings = []
    scores = []

    organic_pct = g.get("organic_signup_pct")
    if organic_pct is not None:
        s = score_between(organic_pct, 0.05, 0.50)
        scores.append(s)
        if organic_pct >= 0.30:
            findings.append(f"✓ {organic_pct:.0%} organic signups — word of mouth is working")
        elif organic_pct >= 0.20:
            findings.append(f"◑ {organic_pct:.0%} organic — moderate. Build referral loop deliberately.")
        else:
            findings.append(f"✗ {organic_pct:.0%} organic — almost all paid. PMF may not be strong enough to generate word of mouth.")
    else:
        findings.append("⚠ No organic signup tracking. Tag all signup sources now.")

    referral = g.get("referral_rate")
    if referral is not None:
        s = score_between(referral, 0.05, 0.35)
        scores.append(s)
        if referral >= 0.25:
            findings.append(f"✓ {referral:.0%} of active users referring — strong viral signal")
        elif referral >= 0.15:
            findings.append(f"◑ {referral:.0%} referral rate — building. Add referral incentive or friction removal.")
        else:
            findings.append(f"✗ {referral:.0%} referral rate — users not recommending. Satisfaction or network effects missing.")
    else:
        findings.append("⚠ No referral rate data.")

    mom = g.get("mom_growth_rate")
    if mom is not None:
        s = score_between(mom, 0, 0.20)
        scores.append(s)
        if mom >= 0.15:
            findings.append(f"✓ {mom:.0%} MoM growth — strong momentum")
        elif mom >= 0.08:
            findings.append(f"◑ {mom:.0%} MoM growth — moderate. Identify top acquisition channel and double it.")
        else:
            findings.append(f"✗ {mom:.0%} MoM growth — slow. Acquisition is a bottleneck.")

    if not scores:
        return 0.0, findings
    return clamp(sum(scores) / len(scores)), findings
def pmf_status(overall: float) -> tuple[str, str]:
    """Returns (status label, description)."""
    if overall >= 0.80:
        return "STRONG PMF", "Clear product-market fit. Shift focus to scaling acquisition and defending moat."
    elif overall >= 0.60:
        return "PMF APPROACHING", "Meaningful signals present. Identify and remove the 1-2 friction points blocking retention."
    elif overall >= 0.40:
        return "EARLY SIGNALS", "Weak PMF. Some users find value. Narrow your ICP and double down on what's working."
    elif overall >= 0.20:
        return "PRE-PMF", "No clear PMF yet. Don't scale acquisition. Focus entirely on retention experiments."
    else:
        return "NO SIGNAL", "No PMF signals detected. Revisit the problem hypothesis before investing further in the solution."
