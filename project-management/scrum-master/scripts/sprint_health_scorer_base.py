# ruff: noqa: E501
#!/usr/bin/env python3
"""
Sprint Health Scorer

Scores sprint health across multiple dimensions including commitment reliability,
scope creep, blocker resolution time, ceremony attendance, and story completion
distribution. Produces composite health scores with actionable recommendations.

Usage:
    python sprint_health_scorer.py sprint_data.json
    python sprint_health_scorer.py sprint_data.json --format json
"""

import argparse
import json
import statistics
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Scoring Configuration
# ---------------------------------------------------------------------------

__all__ = ['Any', 'Dict', 'List', 'Optional', 'Tuple', 'argparse', 'datetime', 'json', 'statistics', 'sys', 'timedelta']
