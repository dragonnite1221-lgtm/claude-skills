# ruff: noqa: E501
#!/usr/bin/env python3
"""
referral_roi_calculator.py — Calculates referral program ROI.

Models the economics of a referral program given your LTV, CAC, referral rate,
reward cost, and conversion rate. Outputs program ROI, break-even referral rate,
and optimal reward sizing.

Usage:
    python3 referral_roi_calculator.py                    # runs embedded sample
    python3 referral_roi_calculator.py params.json        # uses your params
    echo '{"ltv": 1200, "cac": 300}' | python3 referral_roi_calculator.py

JSON input format:
    {
        "ltv": 1200,               # Customer Lifetime Value ($)
        "cac": 300,                # Current avg CAC via paid channels ($)
        "active_users": 500,       # Active users who could refer
        "referral_rate": 0.05,     # % of active users who refer each month (0.05 = 5%)
        "referrals_per_referrer": 2.5,  # Avg referrals sent per active referrer
        "referral_conversion_rate": 0.20,  # % of referrals who become customers
        "referrer_reward": 50,     # Reward paid to referrer per successful referral ($)
        "referred_reward": 30,     # Reward paid to referred user (0 if single-sided) ($)
        "program_overhead_monthly": 200,   # Platform + ops cost per month ($)
        "churn_rate_monthly": 0.03,        # Monthly churn rate (used for LTV validation)
        "months_to_model": 12              # How many months to project
    }
"""

import json
import sys
from collections import OrderedDict


# ---------------------------------------------------------------------------
# Core calculation functions
# ---------------------------------------------------------------------------

__all__ = ['OrderedDict', 'json', 'sys']
