# ruff: noqa: E501
#!/usr/bin/env python3
"""
Resource Capacity Planner

Models team capacity across projects, identifies over/under-allocation, simulates
"what-if" scenarios for adding/removing resources, calculates utilization rates,
and provides capacity optimization recommendations for project portfolios.

Usage:
    python resource_capacity_planner.py capacity_data.json
    python resource_capacity_planner.py capacity_data.json --format json
"""

import argparse
import json
import statistics
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union


# ---------------------------------------------------------------------------
# Capacity Planning Configuration
# ---------------------------------------------------------------------------

__all__ = ['Any', 'Dict', 'List', 'Optional', 'Tuple', 'Union', 'argparse', 'datetime', 'json', 'statistics', 'sys', 'timedelta']
