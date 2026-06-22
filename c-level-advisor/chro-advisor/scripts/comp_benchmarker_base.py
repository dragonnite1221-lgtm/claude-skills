# ruff: noqa: E501
#!/usr/bin/env python3
"""
Compensation Benchmarker
========================
Salary benchmarking and total comp modeling for startup teams.
Analyzes pay equity, compa-ratios, and total comp vs. market.

Usage:
    python comp_benchmarker.py                       # Run with built-in sample data
    python comp_benchmarker.py --config roster.json  # Load from JSON
    python comp_benchmarker.py --help

Output: Band compliance report, compa-ratio distribution, pay equity flags,
        equity value analysis, and total comp vs. market.
"""

import argparse
import json
import csv
import io
import sys
from dataclasses import dataclass, field, asdict
from typing import Optional
from datetime import date
import math


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

__all__ = ['Optional', 'argparse', 'asdict', 'csv', 'dataclass', 'date', 'field', 'io', 'json', 'math', 'sys']
