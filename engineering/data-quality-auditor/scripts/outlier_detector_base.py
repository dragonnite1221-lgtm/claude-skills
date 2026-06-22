# ruff: noqa: E501
#!/usr/bin/env python3
from __future__ import annotations
"""
outlier_detector.py — Multi-method outlier detection for numeric columns.

Methods:
  iqr     — Interquartile Range (robust, non-parametric, default)
  zscore  — Standard Z-score (assumes normal distribution)
  mzscore — Modified Z-score via Median Absolute Deviation (robust to skew)

Usage:
    python3 outlier_detector.py --file data.csv
    python3 outlier_detector.py --file data.csv --method iqr
    python3 outlier_detector.py --file data.csv --method zscore --threshold 2.5
    python3 outlier_detector.py --file data.csv --columns col1,col2
    python3 outlier_detector.py --file data.csv --format json
"""

import argparse
import csv
import json
import math
import sys

__all__ = ['annotations', 'argparse', 'csv', 'json', 'math', 'sys']
