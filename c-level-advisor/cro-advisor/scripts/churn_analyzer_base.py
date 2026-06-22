# ruff: noqa: E501
#!/usr/bin/env python3
"""
Churn & Retention Analyzer
===========================
Customer-level churn and Net Revenue Retention (NRR) analysis for B2B SaaS.

Calculates:
  - Gross Revenue Retention (GRR) and Net Revenue Retention (NRR)
  - Monthly and annual churn rates (logo + revenue)
  - Cohort-based retention curves
  - At-risk account identification
  - Expansion revenue segmentation
  - ARR waterfall (new / expansion / contraction / churn)

Usage:
  python churn_analyzer.py
  python churn_analyzer.py --csv customers.csv
  python churn_analyzer.py --period 2026-Q1 --output summary

Input format (CSV):
  customer_id, name, segment, arr, start_date, [churn_date], [expansion_arr], [contraction_arr]

Stdlib only. No dependencies.
"""

import csv
import sys
import json
import argparse
import statistics
from datetime import date, datetime, timedelta
from collections import defaultdict
from io import StringIO
from itertools import groupby


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

__all__ = ['StringIO', 'argparse', 'csv', 'date', 'datetime', 'defaultdict', 'groupby', 'json', 'statistics', 'sys', 'timedelta']
