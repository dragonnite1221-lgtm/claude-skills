# ruff: noqa: E501
#!/usr/bin/env python3
"""
social_calendar_generator.py — Social Media Content Calendar Generator
100% stdlib, no pip installs required.

Usage:
    python3 social_calendar_generator.py                       # demo mode
    python3 social_calendar_generator.py --config config.json
    python3 social_calendar_generator.py --config config.json --json
    python3 social_calendar_generator.py --config config.json --markdown > calendar.md
    python3 social_calendar_generator.py --start 2026-04-01 --weeks 4

config.json format:
    {
      "pillars": [
        {"name": "Educational",    "description": "Tips, tutorials, how-tos", "emoji": "🎓", "weight": 3},
        {"name": "Inspirational",  "description": "Success stories, quotes",  "emoji": "✨", "weight": 2},
        {"name": "Product",        "description": "Features, demos",          "emoji": "🛠", "weight": 2},
        {"name": "Community",      "description": "UGC, shoutouts, polls",    "emoji": "🤝", "weight": 1}
      ],
      "platforms": [
        {"name": "LinkedIn",  "posts_per_week": 3, "best_days": ["Monday","Tuesday","Wednesday","Thursday"]},
        {"name": "Twitter/X", "posts_per_week": 5, "best_days": ["Monday","Tuesday","Wednesday","Thursday","Friday"]}
      ],
      "start_date": "2026-04-07",
      "weeks": 4
    }
"""

import argparse
import json
import sys
from datetime import date, timedelta
from collections import defaultdict


# ---------------------------------------------------------------------------
# Defaults / sample data
# ---------------------------------------------------------------------------

__all__ = ['argparse', 'date', 'defaultdict', 'json', 'sys', 'timedelta']
