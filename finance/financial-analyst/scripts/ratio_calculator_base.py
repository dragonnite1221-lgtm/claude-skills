# ruff: noqa: F403, F405, E501
"""
Financial Ratio Calculator

Calculates and interprets financial ratios across 5 categories:
profitability, liquidity, leverage, efficiency, and valuation.

Usage:
    python ratio_calculator.py financial_data.json
    python ratio_calculator.py financial_data.json --format json
    python ratio_calculator.py financial_data.json --category profitability
"""
import argparse
import json
import sys
from typing import Any, Dict, List, Optional, Tuple


# fmt: off
__all__ = ['Any', 'Dict', 'List', 'Optional', 'Tuple', 'argparse', 'json', 'sys']  # noqa: E501
# fmt: on
