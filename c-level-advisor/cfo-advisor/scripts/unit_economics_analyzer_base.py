# ruff: noqa: E501
#!/usr/bin/env python3
"""
Unit Economics Analyzer
========================
Per-cohort LTV, per-channel CAC, payback periods, and LTV:CAC ratios.
Never blended averages — those hide what's actually happening.

Usage:
    python unit_economics_analyzer.py
    python unit_economics_analyzer.py --csv

Stdlib only. No dependencies.
"""

import argparse
import csv
import io
import sys
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

__all__ = ['Optional', 'argparse', 'csv', 'dataclass', 'field', 'io', 'sys']
