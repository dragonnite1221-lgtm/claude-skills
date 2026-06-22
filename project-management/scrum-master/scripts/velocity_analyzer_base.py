# ruff: noqa: E501
#!/usr/bin/env python3
"""
Sprint Velocity Analyzer

Analyzes sprint velocity data to calculate rolling averages, detect trends, forecast
capacity, and identify anomalies. Supports multiple statistical measures and 
probabilistic forecasting for scrum teams.

Usage:
    python velocity_analyzer.py sprint_data.json
    python velocity_analyzer.py sprint_data.json --format json
"""

import argparse
import json
import math
import statistics
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union


# ---------------------------------------------------------------------------
# Constants and Configuration
# ---------------------------------------------------------------------------

__all__ = ['Any', 'Dict', 'List', 'Optional', 'Tuple', 'Union', 'argparse', 'datetime', 'json', 'math', 'statistics', 'sys', 'timedelta']
