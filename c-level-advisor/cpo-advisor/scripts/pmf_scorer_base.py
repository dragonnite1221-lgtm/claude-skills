# ruff: noqa: E501
#!/usr/bin/env python3
"""
PMF Scorer — Multi-dimensional Product-Market Fit analysis.

Scores PMF across four dimensions:
  - Retention   (40%): D30 and D90 cohort retention
  - Engagement  (25%): DAU/MAU, session depth, key action rate
  - Satisfaction(20%): Sean Ellis score, NPS
  - Growth      (15%): Organic signup rate, referral rate

Usage:
    python pmf_scorer.py                    # Run with built-in sample data
    python pmf_scorer.py --input data.json  # Run with your data

JSON input format: see sample_data() function below.
"""

import json
import sys
import argparse
import math
from typing import Optional


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

__all__ = ['Optional', 'argparse', 'json', 'math', 'sys']
