# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from tracking_plan_generator_base import *  # noqa: F403,E402


SAMPLE_INPUT = {
    "business_type": "saas",
    "key_pages": [
        {"name": "Homepage", "path": "/"},
        {"name": "Pricing", "path": "/pricing"},
        {"name": "Signup", "path": "/signup"},
        {"name": "Dashboard", "path": "/app/dashboard"},
        {"name": "Onboarding", "path": "/app/onboarding"}
    ],
    "conversion_actions": [
        {"name": "Signup", "type": "registration", "value": 0},
        {"name": "Trial Start", "type": "trial", "value": 0},
        {"name": "Subscription Purchase", "type": "purchase", "value": 99},
        {"name": "Demo Request", "type": "lead", "value": 0}
    ],
    "paid_channels": ["google_ads", "meta"],
    "consent_required": True
}
