# ruff: noqa: E501
#!/usr/bin/env python3
"""
tool_roi_estimator.py — Estimates ROI of building a free marketing tool.

Models the return from a free tool given build cost, maintenance, expected traffic,
conversion rate, and lead value. Outputs ROI timeline, break-even month, and
minimum traffic needed to justify the investment.

Usage:
    python3 tool_roi_estimator.py                    # runs embedded sample
    python3 tool_roi_estimator.py params.json        # uses your params
    echo '{"build_cost": 5000, "lead_value": 200}' | python3 tool_roi_estimator.py

JSON input format:
    {
        "build_cost": 5000,              # One-time engineering cost ($) — dev time × rate
        "monthly_maintenance": 150,      # Ongoing server, API, ops cost per month ($)
        "traffic_month_1": 500,          # Expected organic sessions in month 1
        "traffic_growth_rate": 0.15,     # Monthly organic traffic growth rate (0.15 = 15%)
        "tool_completion_rate": 0.55,    # % of visitors who complete the tool (0.55 = 55%)
        "lead_capture_rate": 0.10,       # % of completions who give email (0.10 = 10%)
        "lead_to_trial_rate": 0.08,      # % of leads who start a trial
        "trial_to_paid_rate": 0.25,      # % of trials who become paid customers
        "ltv": 1200,                     # Customer LTV ($)
        "months_to_model": 24,           # How many months to project
        "seo_ramp_months": 3,            # Months before organic traffic kicks in (0 if PH/HN spike)
        "backlink_value_monthly": 200,   # Estimated value of earned backlinks (DA × niche rate)
        "tool_name": "ROI Calculator"    # For display only
    }
"""

import json
import math
import sys


# ---------------------------------------------------------------------------
# Core calculations
# ---------------------------------------------------------------------------

__all__ = ['json', 'math', 'sys']
