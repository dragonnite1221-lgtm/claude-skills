# ruff: noqa: E501
#!/usr/bin/env python3
"""
sample_size_calculator.py — A/B Test Sample Size Calculator
100% stdlib, no pip installs required.

Usage:
    python3 sample_size_calculator.py                          # demo mode
    python3 sample_size_calculator.py --baseline 0.05 --mde 0.20
    python3 sample_size_calculator.py --baseline 0.05 --mde 0.20 --daily-traffic 500
    python3 sample_size_calculator.py --baseline 0.05 --mde 0.20 --json
"""

import argparse
import json
import math
import sys


# ---------------------------------------------------------------------------
# Z-score approximation (scipy-free, Beasley-Springer-Moro algorithm)
# ---------------------------------------------------------------------------

__all__ = ['argparse', 'json', 'math', 'sys']
