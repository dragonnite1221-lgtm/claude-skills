# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from seo_health_scorer_base import *  # noqa: F403,E402


DEFAULT_WEIGHTS = {
    "technical": 0.22,
    "content": 0.23,
    "on_page": 0.20,
    "schema": 0.10,
    "performance": 0.10,
    "ai_readiness": 0.10,
    "images": 0.05,
}
INDUSTRY_ADJUSTMENTS = {
    "saas": {"technical": 0.05, "content": 0.05, "schema": -0.05, "images": -0.05},
    "ecommerce": {"schema": 0.05, "images": 0.05, "ai_readiness": -0.05, "content": -0.05},
    "local": {"on_page": 0.05, "schema": 0.05, "technical": -0.05, "ai_readiness": -0.05},
    "publisher": {"content": 0.05, "ai_readiness": 0.05, "technical": -0.05, "schema": -0.05},
}
RESULT_SCORES = {"pass": 1.0, "warn": 0.5, "fail": 0.0}
SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}
DEMO_CHECKS = [
    {"category": "technical", "check": "robots.txt exists", "result": "pass", "severity": "critical"},
    {"category": "technical", "check": "sitemap.xml valid", "result": "pass", "severity": "critical"},
    {"category": "technical", "check": "no redirect chains", "result": "warn", "severity": "high", "detail": "2 chains found (3-hop)"},
    {"category": "technical", "check": "canonical tags present", "result": "pass", "severity": "high"},
    {"category": "technical", "check": "mobile-friendly", "result": "pass", "severity": "critical"},
    {"category": "content", "check": "no thin pages (<300 words)", "result": "fail", "severity": "high", "detail": "8 pages under 300 words"},
    {"category": "content", "check": "no duplicate titles", "result": "pass", "severity": "medium"},
    {"category": "content", "check": "no keyword stuffing", "result": "pass", "severity": "medium"},
    {"category": "content", "check": "readability (Flesch 60-70)", "result": "warn", "severity": "low", "detail": "avg Flesch 52"},
    {"category": "on_page", "check": "title tags 50-60 chars", "result": "warn", "severity": "high", "detail": "4 pages over 60 chars"},
    {"category": "on_page", "check": "meta descriptions 150-160", "result": "fail", "severity": "medium", "detail": "12 pages missing meta description"},
    {"category": "on_page", "check": "H1 tags present and unique", "result": "pass", "severity": "high"},
    {"category": "on_page", "check": "internal linking (min 3 per page)", "result": "warn", "severity": "medium", "detail": "6 pages have <3 internal links"},
    {"category": "on_page", "check": "all images have alt text", "result": "fail", "severity": "medium", "detail": "23 images missing alt"},
    {"category": "schema", "check": "JSON-LD Organization schema", "result": "pass", "severity": "medium"},
    {"category": "schema", "check": "breadcrumb schema", "result": "fail", "severity": "medium", "detail": "no breadcrumb markup found"},
    {"category": "schema", "check": "article/product schema", "result": "pass", "severity": "medium"},
    {"category": "performance", "check": "LCP < 2.5s", "result": "pass", "severity": "critical"},
    {"category": "performance", "check": "CLS < 0.1", "result": "warn", "severity": "high", "detail": "CLS 0.14 on mobile"},
    {"category": "performance", "check": "INP < 200ms", "result": "pass", "severity": "high"},
    {"category": "ai_readiness", "check": "answer-first paragraphs", "result": "fail", "severity": "medium", "detail": "most H2s don't start with a direct answer"},
    {"category": "ai_readiness", "check": "entity clarity", "result": "warn", "severity": "low", "detail": "ambiguous entity references on 3 pages"},
    {"category": "images", "check": "WebP/AVIF format", "result": "warn", "severity": "low", "detail": "14 images still JPEG"},
    {"category": "images", "check": "lazy loading", "result": "pass", "severity": "medium"},
]
def get_weights(industry=None):
    weights = dict(DEFAULT_WEIGHTS)
    if industry and industry in INDUSTRY_ADJUSTMENTS:
        for cat, adj in INDUSTRY_ADJUSTMENTS[industry].items():
            weights[cat] = weights.get(cat, 0) + adj
    return weights
def score_checks(checks, industry=None):
    weights = get_weights(industry)
    by_category = defaultdict(list)
    for c in checks:
        cat = c.get("category", "other").lower().replace("-", "_").replace(" ", "_")
        by_category[cat].append(c)

    category_scores = {}
    all_findings = []

    for cat, cat_checks in by_category.items():
        if not cat_checks:
            continue
        total = 0.0
        for check in cat_checks:
            result = check.get("result", "fail").lower()
            total += RESULT_SCORES.get(result, 0.0)
            if result != "pass":
                all_findings.append({
                    "category": cat,
                    "check": check.get("check", ""),
                    "result": result,
                    "severity": check.get("severity", "medium"),
                    "detail": check.get("detail", ""),
                })
        cat_score = (total / len(cat_checks)) * 100 if cat_checks else 100
        category_scores[cat] = round(cat_score, 1)

    # Weighted overall score
    overall = 0.0
    total_weight = 0.0
    for cat, weight in weights.items():
        if cat in category_scores:
            overall += category_scores[cat] * weight
            total_weight += weight

    if total_weight > 0:
        overall = overall / total_weight
    else:
        overall = 0.0

    # Sort findings by severity
    all_findings.sort(key=lambda f: SEVERITY_ORDER.get(f["severity"], 99))

    # Quick wins: high/critical severity + likely fast fix
    quick_wins = [f for f in all_findings if f["severity"] in ("critical", "high") and f["result"] == "warn"]

    # Grade
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

    return {
        "overall_score": round(overall, 1),
        "grade": grade,
        "industry": industry or "general",
        "weights_used": {k: round(v, 2) for k, v in weights.items()},
        "category_scores": category_scores,
        "total_checks": len(checks),
        "passed": sum(1 for c in checks if c.get("result") == "pass"),
        "warnings": sum(1 for c in checks if c.get("result") == "warn"),
        "failures": sum(1 for c in checks if c.get("result") == "fail"),
        "findings": all_findings,
        "quick_wins": quick_wins,
        "action_plan": {
            "critical": [f for f in all_findings if f["severity"] == "critical"],
            "high": [f for f in all_findings if f["severity"] == "high"],
            "medium": [f for f in all_findings if f["severity"] == "medium"],
            "low": [f for f in all_findings if f["severity"] == "low"],
        },
    }
