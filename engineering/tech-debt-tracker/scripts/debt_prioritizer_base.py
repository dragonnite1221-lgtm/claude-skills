# ruff: noqa: F403, F405, E501
"""
Tech Debt Prioritizer

Takes a debt inventory (from scanner or manual JSON) and calculates interest rate,
effort estimates, and produces a prioritized backlog with recommended sprint allocation.
Uses cost-of-delay vs effort scoring and various prioritization frameworks.

Usage:
    python debt_prioritizer.py debt_inventory.json
    python debt_prioritizer.py debt_inventory.json --output prioritized_backlog.json
    python debt_prioritizer.py debt_inventory.json --team-size 6 --sprint-capacity 80
    python debt_prioritizer.py debt_inventory.json --framework wsjf --output results.json
"""
import json
import argparse
import sys
import math
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict


# fmt: off
__all__ = ['Any', 'Counter', 'Dict', 'List', 'Optional', 'Tuple', 'argparse', 'asdict', 'dataclass', 'datetime', 'defaultdict', 'json', 'math', 'sys', 'timedelta']  # noqa: E501
# fmt: on
