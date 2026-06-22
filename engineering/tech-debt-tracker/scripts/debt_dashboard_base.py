# ruff: noqa: F403, F405, E501
"""
Tech Debt Dashboard

Takes historical debt inventories (multiple scans over time) and generates trend analysis,
debt velocity (accruing vs paying down), health score, and executive summary.

Usage:
    python debt_dashboard.py historical_data.json
    python debt_dashboard.py data1.json data2.json data3.json
    python debt_dashboard.py --input-dir ./debt_scans/ --output dashboard_report.json
    python debt_dashboard.py historical_data.json --period quarterly --team-size 8
"""
import json
import argparse
import sys
import os
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from statistics import mean, median, stdev
import re


# fmt: off
__all__ = ['Any', 'Counter', 'Dict', 'List', 'Optional', 'Path', 'Tuple', 'argparse', 'asdict', 'dataclass', 'datetime', 'defaultdict', 'json', 'mean', 'median', 'os', 're', 'stdev', 'sys', 'timedelta']  # noqa: E501
# fmt: on
