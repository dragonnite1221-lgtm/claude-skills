# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from launch_readiness_scorer_base import *  # noqa: F403,E402


DEFAULT_CHECKLIST = {
    "product": [
        {"item": "Beta tested with real users (≥10)",          "status": "done",        "weight": 3},
        {"item": "Core user journey validated end-to-end",     "status": "done",        "weight": 3},
        {"item": "Known P0/P1 bugs resolved",                  "status": "partial",     "weight": 3},
        {"item": "User-facing documentation complete",         "status": "partial",     "weight": 2},
        {"item": "In-app onboarding / empty states ready",     "status": "done",        "weight": 2},
        {"item": "Support team trained on common Q&A",         "status": "not_started", "weight": 2},
        {"item": "Pricing finalised and live",                  "status": "done",        "weight": 2},
        {"item": "Accessibility basics checked (WCAG AA)",     "status": "not_started", "weight": 1},
        {"item": "Localisation / i18n ready (if applicable)",  "status": "done",        "weight": 1},
        {"item": "Feedback collection mechanism in place",     "status": "partial",     "weight": 1},
    ],
    "marketing": [
        {"item": "Landing page live and conversion-optimised", "status": "done",        "weight": 3},
        {"item": "Email announcement list ready (≥100)",       "status": "done",        "weight": 3},
        {"item": "Press / media kit prepared",                  "status": "partial",     "weight": 2},
        {"item": "Social media assets created",                 "status": "done",        "weight": 2},
        {"item": "Product Hunt / launch platform submission",  "status": "not_started", "weight": 2},
        {"item": "SEO meta tags and OG images set",            "status": "done",        "weight": 2},
        {"item": "Influencer / community outreach planned",    "status": "partial",     "weight": 2},
        {"item": "Launch-day email sequence scheduled",        "status": "not_started", "weight": 2},
        {"item": "Paid ads creative prepared (if applicable)", "status": "not_started", "weight": 1},
        {"item": "Referral / viral loop mechanism designed",   "status": "not_started", "weight": 1},
    ],
    "technical": [
        {"item": "Production monitoring & alerting active",    "status": "done",        "weight": 3},
        {"item": "Load / performance tested at 5× expected",  "status": "partial",     "weight": 3},
        {"item": "Rollback plan documented and rehearsed",     "status": "not_started", "weight": 3},
        {"item": "Database backups verified and automated",    "status": "done",        "weight": 2},
        {"item": "CDN / caching configured",                   "status": "done",        "weight": 2},
        {"item": "Error tracking (Sentry/similar) live",       "status": "done",        "weight": 2},
        {"item": "SSL / HTTPS confirmed on all endpoints",     "status": "done",        "weight": 2},
        {"item": "Analytics events firing correctly",          "status": "partial",     "weight": 2},
        {"item": "Rate limiting / DDoS protection in place",   "status": "partial",     "weight": 2},
        {"item": "Feature flags configured for safe rollout",  "status": "not_started", "weight": 1},
    ],
}
CATEGORY_META = {
    "product":   {"emoji": "🛠 ", "label": "Product Readiness"},
    "marketing": {"emoji": "📣 ", "label": "Marketing Readiness"},
    "technical": {"emoji": "⚙️ ", "label": "Technical Readiness"},
}
STATUS_WEIGHTS = {
    "done":        1.0,
    "partial":     0.5,
    "not_started": 0.0,
}
BLOCKERS_THRESHOLD = 0.0   # not_started items with weight ≥3 are blockers
def _score_label(s: int) -> str:
    if s >= 90: return "Excellent"
    if s >= 75: return "Good"
    if s >= 60: return "Fair"
    if s >= 40: return "Poor"
    return "Critical"
def score_category(items: list) -> dict:
    """Score a single category 0-100 using weighted item scores."""
    if not items:
        return {"score": 0, "items": [], "blockers": []}

    total_weight  = 0
    earned_weight = 0
    blockers      = []
    scored_items  = []

    for it in items:
        raw_status = it.get("status", "not_started").strip().lower()
        status     = raw_status if raw_status in STATUS_WEIGHTS else "not_started"
        weight     = it.get("weight", 1)
        sw         = STATUS_WEIGHTS[status]
        earned     = sw * weight

        total_weight  += weight
        earned_weight += earned

        scored_items.append({
            "item":           it["item"],
            "status":         status,
            "weight":         weight,
            "points_earned":  earned,
            "points_max":     weight,
        })

        if status == "not_started" and weight >= 3:
            blockers.append(it["item"])

    score = round((earned_weight / total_weight) * 100) if total_weight > 0 else 0
    return {
        "score":          score,
        "score_label":    _score_label(score),
        "items":          scored_items,
        "blockers":       blockers,
        "items_done":     sum(1 for i in scored_items if i["status"] == "done"),
        "items_partial":  sum(1 for i in scored_items if i["status"] == "partial"),
        "items_pending":  sum(1 for i in scored_items if i["status"] == "not_started"),
        "total_items":    len(scored_items),
    }
def _launch_decision(score: int, blockers: list) -> str:
    if blockers:
        return f"⛔  NOT READY — {len(blockers)} blocker(s) must be resolved before launch."
    if score >= 80:
        return "✅  LAUNCH READY — all categories are in good shape."
    if score >= 60:
        return "🟡  CONDITIONAL — address partial items but launch is defensible."
    if score >= 40:
        return "🟠  CAUTION — significant gaps; soft launch / waitlist recommended."
    return "🔴  NOT READY — major preparation required across multiple areas."
def _action_plan(categories: dict) -> list:
    """Build a prioritised action list: blockers first, then by score ascending."""
    actions = []
    for cat, res in categories.items():
        label = CATEGORY_META.get(cat, {}).get("label", cat.title())
        for bl in res.get("blockers", []):
            actions.append({
                "priority":  "🚨 BLOCKER",
                "category":  label,
                "action":    bl,
            })
    for cat, res in sorted(categories.items(), key=lambda x: x[1]["score"]):
        label = CATEGORY_META.get(cat, {}).get("label", cat.title())
        for it in res.get("items", []):
            if it["status"] == "partial":
                actions.append({
                    "priority": "⚠️  PARTIAL",
                    "category": label,
                    "action":   f"Complete: {it['item']}",
                })
    return actions[:15]   # top 15 actions
