# ruff: noqa: E501
#!/usr/bin/env python3
"""
Burn Rate & Runway Calculator
==============================
Models startup runway across base/bull/bear scenarios, incorporating
a hiring plan and revenue trajectory. Outputs months of runway,
cash-out dates, and decision trigger points.

Usage:
    python burn_rate_calculator.py
    python burn_rate_calculator.py --csv  # export to CSV

Stdlib only. No dependencies.
"""

import argparse
import csv
import io
import sys
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Optional


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

__all__ = ['Optional', 'argparse', 'csv', 'dataclass', 'date', 'field', 'io', 'sys', 'timedelta']
