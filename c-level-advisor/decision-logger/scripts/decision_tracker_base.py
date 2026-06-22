# ruff: noqa: E501
#!/usr/bin/env python3
"""
decision_tracker.py — Board Meeting Decision Parser & Reporter
Part of the C-Level Advisor / Decision Logger skill.

Parses memory/board-meetings/decisions.md and produces actionable reports.
Stdlib only. No dependencies.

Usage:
    python decision_tracker.py --summary
    python decision_tracker.py --overdue
    python decision_tracker.py --conflicts
    python decision_tracker.py --owner "CMO"
    python decision_tracker.py --search "pricing"
    python decision_tracker.py --due-within 7
    python decision_tracker.py --demo          # Run with sample data
"""

import argparse
import os
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional


# ─────────────────────────────────────────────
# Data structures
# ─────────────────────────────────────────────

__all__ = ['Optional', 'Path', 'argparse', 'date', 'datetime', 'os', 're', 'sys', 'timedelta']
