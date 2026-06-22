# ruff: noqa: E501
#!/usr/bin/env python3
"""
X/Twitter Content Planner — Generate weekly posting calendars.

Creates structured content plans with topic suggestions, format mix,
optimal posting times, and engagement targets.

Usage:
    python3 content_planner.py --niche "AI engineering" --frequency 5 --weeks 2
    python3 content_planner.py --niche "SaaS growth" --frequency 3 --weeks 1 --json
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict

__all__ = ['argparse', 'asdict', 'dataclass', 'datetime', 'field', 'json', 'sys', 'timedelta']
