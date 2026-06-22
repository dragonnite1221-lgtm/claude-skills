# ruff: noqa: E501
#!/usr/bin/env python3
"""
roas_calculator.py — ROAS and paid-ads metrics calculator
Usage:
  python3 roas_calculator.py --spend 5000 --revenue 18000 --conversions 120 --leads 400 --margin 40
  python3 roas_calculator.py --file campaign.json
  python3 roas_calculator.py --json          # demo + JSON output
  python3 roas_calculator.py                 # demo mode
"""

import argparse
import json
import sys


# ---------------------------------------------------------------------------
# Calculation core
# ---------------------------------------------------------------------------

__all__ = ['argparse', 'json', 'sys']
