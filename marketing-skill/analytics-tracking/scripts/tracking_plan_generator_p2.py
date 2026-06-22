# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from tracking_plan_generator_base import *  # noqa: F403,E402


EVENT_TEMPLATES = {
    "saas": {
        "acquisition": [
            {
                "event": "pricing_viewed",
                "trigger": "User navigates to /pricing",
                "parameters": ["page_location", "utm_source", "referrer_page"],
                "priority": "high"
            },
            {
                "event": "demo_requested",
                "trigger": "User submits demo request form",
                "parameters": ["source", "page_location", "form_name"],
                "priority": "high",
                "is_conversion": True
            },
            {
                "event": "content_downloaded",
                "trigger": "User downloads gated content",
                "parameters": ["content_name", "content_type", "gated"],
                "priority": "medium"
            }
        ],
        "registration": [
            {
                "event": "signup_started",
                "trigger": "User clicks primary signup CTA",
                "parameters": ["page_location", "cta_text", "plan_name"],
                "priority": "high"
            },
            {
                "event": "signup_completed",
                "trigger": "User account successfully created",
                "parameters": ["method", "user_id", "plan_name"],
                "priority": "critical",
                "is_conversion": True
            },
            {
                "event": "trial_started",
                "trigger": "Free trial begins",
                "parameters": ["plan_name", "trial_length_days", "user_id"],
                "priority": "critical",
                "is_conversion": True
            }
        ],
        "onboarding": [
            {
                "event": "onboarding_started",
                "trigger": "User enters onboarding flow",
                "parameters": ["user_id", "onboarding_variant"],
                "priority": "high"
            },
            {
                "event": "onboarding_step_completed",
                "trigger": "User completes each onboarding step",
                "parameters": ["step_name", "step_number", "user_id", "time_spent_seconds"],
                "priority": "high"
            },
            {
                "event": "onboarding_completed",
                "trigger": "User completes full onboarding",
                "parameters": ["steps_total", "user_id", "time_to_complete_seconds"],
                "priority": "high"
            },
            {
                "event": "feature_activated",
                "trigger": "User activates a key feature for first time",
                "parameters": ["feature_name", "user_id", "activation_method"],
                "priority": "medium"
            }
        ],
        "conversion": [
            {
                "event": "plan_selected",
                "trigger": "User clicks on a pricing plan",
                "parameters": ["plan_name", "billing_period", "value"],
                "priority": "critical"
            },
            {
                "event": "checkout_started",
                "trigger": "User enters checkout flow",
                "parameters": ["plan_name", "value", "currency", "billing_period"],
                "priority": "critical"
            },
            {
                "event": "checkout_completed",
                "trigger": "Payment successfully processed",
                "parameters": ["plan_name", "value", "currency", "transaction_id", "billing_period"],
                "priority": "critical",
                "is_conversion": True
            }
        ],
        "retention": [
            {
                "event": "subscription_cancelled",
                "trigger": "User confirms cancellation",
                "parameters": ["cancel_reason", "plan_name", "save_offer_shown", "save_offer_accepted"],
                "priority": "high"
            },
            {
                "event": "subscription_reactivated",
                "trigger": "Cancelled user reactivates",
                "parameters": ["plan_name", "days_since_cancel"],
                "priority": "high"
            }
        ]
    },
    "ecommerce": {
        "acquisition": [
            {
                "event": "product_viewed",
                "trigger": "User views a product page",
                "parameters": ["item_id", "item_name", "item_category", "value"],
                "priority": "high"
            },
            {
                "event": "search_performed",
                "trigger": "User submits a search query",
                "parameters": ["search_term", "results_count"],
                "priority": "medium"
            }
        ],
        "conversion": [
            {
                "event": "add_to_cart",
                "trigger": "User adds item to cart",
                "parameters": ["item_id", "item_name", "value", "currency", "quantity"],
                "priority": "critical"
            },
            {
                "event": "checkout_started",
                "trigger": "User begins checkout",
                "parameters": ["value", "currency", "num_items"],
                "priority": "critical"
            },
            {
                "event": "checkout_completed",
                "trigger": "Order placed successfully",
                "parameters": ["transaction_id", "value", "currency", "tax", "shipping"],
                "priority": "critical",
                "is_conversion": True
            }
        ]
    }
}
