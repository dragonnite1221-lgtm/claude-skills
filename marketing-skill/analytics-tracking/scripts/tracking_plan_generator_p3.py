# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from tracking_plan_generator_base import *  # noqa: F403,E402
# fmt: off
from tracking_plan_generator_p2 import EVENT_TEMPLATES  # noqa: E402,E501
# fmt: on


CUSTOM_DIMENSIONS = {
    "user_scoped": [
        {"name": "User ID", "parameter": "user_id", "description": "Internal user identifier"},
        {"name": "Plan Name", "parameter": "plan_name", "description": "Current subscription plan"},
        {"name": "Billing Period", "parameter": "billing_period", "description": "Monthly or annual"},
        {"name": "Signup Method", "parameter": "signup_method", "description": "Email, Google, SSO"},
        {"name": "Onboarding Status", "parameter": "onboarding_completed", "description": "Boolean: completed onboarding?"}
    ],
    "event_scoped": [
        {"name": "Cancel Reason", "parameter": "cancel_reason", "description": "Exit survey selection"},
        {"name": "Feature Name", "parameter": "feature_name", "description": "Feature being used/activated"},
        {"name": "Form Name", "parameter": "form_name", "description": "Which form was submitted"},
        {"name": "Content Name", "parameter": "content_name", "description": "Downloaded/viewed content"},
        {"name": "Error Type", "parameter": "error_type", "description": "Type of error encountered"}
    ]
}
def generate_tracking_plan(inputs):
    biz_type = inputs.get("business_type", "saas")
    templates = EVENT_TEMPLATES.get(biz_type, EVENT_TEMPLATES["saas"])
    paid = inputs.get("paid_channels", [])
    consent = inputs.get("consent_required", False)
    conversions = inputs.get("conversion_actions", [])

    # Build event taxonomy
    all_events = []
    for category, events in templates.items():
        for ev in events:
            all_events.append({**ev, "category": category})

    # Add conversion-specific events from input
    conversion_events = []
    for ca in conversions:
        if ca["type"] == "purchase":
            for ev in all_events:
                if ev["event"] == "checkout_completed":
                    ev["value_hint"] = ca["value"]
            conversion_events.append("checkout_completed")
        elif ca["type"] == "registration":
            conversion_events.append("signup_completed")
        elif ca["type"] == "lead":
            conversion_events.append("demo_requested")
        elif ca["type"] == "trial":
            conversion_events.append("trial_started")

    # GTM tag configuration
    gtm_tags = []
    for ev in all_events:
        gtm_tags.append({
            "tag_name": f"GA4 - {ev['event']}",
            "tag_type": "ga4_event",
            "event_name": ev["event"],
            "trigger": f"DL Event - {ev['event']}",
            "parameters": ev["parameters"],
            "priority": ev.get("priority", "medium")
        })

    # Add platform-specific tags
    if "google_ads" in paid:
        for ev in all_events:
            if ev.get("is_conversion"):
                gtm_tags.append({
                    "tag_name": f"Google Ads - {ev['event']}",
                    "tag_type": "google_ads_conversion",
                    "event_name": ev["event"],
                    "trigger": f"DL Event - {ev['event']}",
                    "note": "Import from GA4 conversions (preferred) or configure conversion ID"
                })

    if "meta" in paid:
        gtm_tags.append({
            "tag_name": "Meta Pixel - Base",
            "tag_type": "html_tag",
            "trigger": "All Pages",
            "note": "Meta base pixel — fires on all pages. Add Standard Events separately."
        })

    # Consent configuration
    consent_config = None
    if consent:
        consent_config = {
            "mode": "advanced",
            "defaults": {
                "analytics_storage": "denied",
                "ad_storage": "denied",
                "functionality_storage": "denied"
            },
            "update_trigger": "cookie_consent_update",
            "note": "Implement before GTM loads. Requires CMP integration (Cookiebot, OneTrust, etc.)."
        }

    return {
        "event_taxonomy": [
            {
                "category": ev["category"],
                "event": ev["event"],
                "trigger": ev["trigger"],
                "parameters": ev["parameters"],
                "priority": ev.get("priority", "medium"),
                "is_conversion": ev.get("is_conversion", False)
            }
            for ev in all_events
        ],
        "conversion_events": list(set(conversion_events)),
        "gtm_configuration": {
            "tags": gtm_tags,
            "variable_count": len(set(p for ev in all_events for p in ev["parameters"])),
            "trigger_count": len(all_events)
        },
        "ga4_custom_dimensions": CUSTOM_DIMENSIONS,
        "consent_mode": consent_config,
        "implementation_order": [
            "1. Register custom dimensions in GA4 (Admin > Custom Definitions)",
            "2. Set up GTM container structure (variables first, then triggers, then tags)",
            "3. Implement dataLayer pushes in application code",
            "4. Test each event in GTM Preview + GA4 DebugView",
            "5. Mark conversion events in GA4 (Admin > Conversions)",
            "6. Link GA4 to Google Ads if running paid search",
            "7. Enable internal traffic filter",
            "8. Implement consent mode if required"
        ]
    }
