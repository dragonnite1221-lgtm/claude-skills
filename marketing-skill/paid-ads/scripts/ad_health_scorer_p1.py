# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from ad_health_scorer_base import *  # noqa: F403,E402


SEVERITY_MULTIPLIER = {"critical": 5.0, "high": 3.0, "medium": 1.5, "low": 0.5}
PLATFORM_WEIGHTS = {
    "google": {
        "conversion_tracking": 0.25,
        "wasted_spend": 0.20,
        "account_structure": 0.15,
        "keywords": 0.15,
        "ads": 0.15,
        "settings": 0.10,
    },
    "meta": {
        "pixel_capi": 0.30,
        "creative": 0.30,
        "structure": 0.20,
        "audience": 0.20,
    },
    "linkedin": {
        "technical": 0.25,
        "targeting": 0.25,
        "creative": 0.25,
        "budget": 0.25,
    },
    "tiktok": {
        "pixel": 0.25,
        "creative": 0.30,
        "targeting": 0.25,
        "budget": 0.20,
    },
}
DEMO_CHECKS = {
    "google": [
        {"category": "conversion_tracking", "check": "Google Ads conversion tag installed", "result": "pass", "severity": "critical"},
        {"category": "conversion_tracking", "check": "Enhanced Conversions enabled", "result": "fail", "severity": "critical", "detail": "Missing enhanced conversions — losing 15-30% attribution"},
        {"category": "conversion_tracking", "check": "Conversion window appropriate", "result": "pass", "severity": "medium"},
        {"category": "wasted_spend", "check": "Negative keyword coverage", "result": "warn", "severity": "high", "detail": "Only 12 negative keywords — review search terms report"},
        {"category": "wasted_spend", "check": "No broad match + manual CPC", "result": "pass", "severity": "critical"},
        {"category": "wasted_spend", "check": "Search terms review (last 30d)", "result": "fail", "severity": "high", "detail": "23% of spend on irrelevant terms"},
        {"category": "account_structure", "check": "Campaign naming convention", "result": "pass", "severity": "low"},
        {"category": "account_structure", "check": "Ad groups ≤ 20 keywords each", "result": "warn", "severity": "medium", "detail": "2 ad groups with 30+ keywords"},
        {"category": "keywords", "check": "No duplicate keywords across campaigns", "result": "pass", "severity": "high"},
        {"category": "keywords", "check": "Quality Score ≥ 6 on top spenders", "result": "warn", "severity": "high", "detail": "3 keywords with QS 4-5"},
        {"category": "ads", "check": "RSA with ≥ 3 headlines", "result": "pass", "severity": "medium"},
        {"category": "ads", "check": "Ad extensions active (sitelinks, callouts)", "result": "fail", "severity": "medium", "detail": "No callout extensions"},
        {"category": "settings", "check": "Location targeting correct", "result": "pass", "severity": "high"},
        {"category": "settings", "check": "Ad schedule aligned with business hours", "result": "pass", "severity": "low"},
    ],
    "meta": [
        {"category": "pixel_capi", "check": "Meta Pixel installed", "result": "pass", "severity": "critical"},
        {"category": "pixel_capi", "check": "Conversions API (CAPI) active", "result": "fail", "severity": "critical", "detail": "No server-side events — degraded attribution post-iOS14"},
        {"category": "creative", "check": "Creative diversity (≥ 3 formats)", "result": "warn", "severity": "high", "detail": "Only static images — add video and carousel"},
        {"category": "creative", "check": "No creative fatigue (CTR stable)", "result": "pass", "severity": "high"},
        {"category": "structure", "check": "CBO enabled", "result": "pass", "severity": "medium"},
        {"category": "audience", "check": "Lookalike seed ≥ 1000 users", "result": "pass", "severity": "medium"},
    ],
}
def score_platform(checks, platform):
    weights = PLATFORM_WEIGHTS.get(platform, {})
    by_category = defaultdict(list)
    for c in checks:
        by_category[c.get("category", "other")].append(c)

    category_scores = {}
    findings = []
    quick_wins = []

    for cat, cat_checks in by_category.items():
        weighted_pass = 0.0
        weighted_total = 0.0
        for check in cat_checks:
            result = check.get("result", "fail")
            severity = check.get("severity", "medium")
            mult = SEVERITY_MULTIPLIER.get(severity, 1.0)
            score = {"pass": 1.0, "warn": 0.5, "fail": 0.0}.get(result, 0.0)
            weighted_pass += score * mult
            weighted_total += mult
            if result != "pass":
                finding = {
                    "platform": platform,
                    "category": cat,
                    "check": check.get("check", ""),
                    "result": result,
                    "severity": severity,
                    "detail": check.get("detail", ""),
                }
                findings.append(finding)
                # Quick win: high/critical severity + warn (not full fail)
                if severity in ("critical", "high") and result == "warn":
                    quick_wins.append(finding)

        cat_score = (weighted_pass / weighted_total * 100) if weighted_total > 0 else 100
        category_scores[cat] = round(cat_score, 1)

    # Weighted overall
    overall = 0.0
    total_weight = 0.0
    for cat, weight in weights.items():
        if cat in category_scores:
            overall += category_scores[cat] * weight
            total_weight += weight
    overall = (overall / total_weight) if total_weight > 0 else 0.0

    if overall >= 90:
        grade = "A"
    elif overall >= 75:
        grade = "B"
    elif overall >= 60:
        grade = "C"
    elif overall >= 40:
        grade = "D"
    else:
        grade = "F"

    findings.sort(key=lambda f: {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(f["severity"], 99))

    return {
        "platform": platform,
        "overall_score": round(overall, 1),
        "grade": grade,
        "category_scores": category_scores,
        "total_checks": len(checks),
        "passed": sum(1 for c in checks if c.get("result") == "pass"),
        "warnings": sum(1 for c in checks if c.get("result") == "warn"),
        "failures": sum(1 for c in checks if c.get("result") == "fail"),
        "findings": findings,
        "quick_wins": quick_wins,
    }
