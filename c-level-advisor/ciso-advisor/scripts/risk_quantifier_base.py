# ruff: noqa: E501
#!/usr/bin/env python3
"""
CISO Risk Quantifier
====================
Quantifies security risks in business terms using the FAIR model.
Calculates ALE (Annual Loss Expectancy) and prioritizes by expected annual loss.

Usage:
  python risk_quantifier.py                    # Run with sample data
  python risk_quantifier.py --json             # Output JSON
  python risk_quantifier.py --csv output.csv   # Export CSV
  python risk_quantifier.py --budget 500000    # Show what fits in budget
  python risk_quantifier.py --add              # Interactive risk entry
"""

import json
import csv
import sys
import os
import argparse
from datetime import datetime
from typing import Optional


# ─── Data Model ─────────────────────────────────────────────────────────────

__all__ = ['Optional', 'argparse', 'csv', 'datetime', 'json', 'os', 'sys']
