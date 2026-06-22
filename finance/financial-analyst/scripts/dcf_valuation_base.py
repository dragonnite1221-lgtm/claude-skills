# ruff: noqa: F403, F405, E501
"""
DCF Valuation Model

Discounted Cash Flow enterprise and equity valuation with WACC calculation,
terminal value estimation, and two-way sensitivity analysis.

Uses standard library only (math, statistics) - NO numpy/pandas/scipy.

Usage:
    python dcf_valuation.py valuation_data.json
    python dcf_valuation.py valuation_data.json --format json
    python dcf_valuation.py valuation_data.json --projection-years 7
"""
import argparse
import json
import math
import sys
from statistics import mean
from typing import Any, Dict, List, Optional, Tuple


# fmt: off
__all__ = ['Any', 'Dict', 'List', 'Optional', 'Tuple', 'argparse', 'json', 'math', 'mean', 'sys']  # noqa: E501
# fmt: on
