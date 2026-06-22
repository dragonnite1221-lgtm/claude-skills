# ruff: noqa: E501
#!/usr/bin/env python3
"""
Activation Funnel Analyzer for Onboarding CRO

Analyzes user onboarding funnel data to identify drop-off points
and estimate the impact of improving each step.

Usage:
  python3 activation_funnel_analyzer.py                    # Demo mode
  python3 activation_funnel_analyzer.py funnel.json        # From data
  python3 activation_funnel_analyzer.py funnel.json --json  # JSON output

Input format (JSON):
{
  "steps": [
    {"name": "Signup completed", "users": 1000},
    {"name": "Email verified", "users": 850},
    {"name": "Profile setup", "users": 620},
    {"name": "First action", "users": 310},
    {"name": "Aha moment", "users": 180},
    {"name": "Activated (Day 7)", "users": 120}
  ]
}
"""

import json
import sys
import os

__all__ = ['json', 'os', 'sys']
