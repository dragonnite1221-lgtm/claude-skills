# ruff: noqa: E501
#!/usr/bin/env python3
from __future__ import annotations
"""
data_profiler.py — Full dataset profile with Data Quality Score (DQS).

Usage:
    python3 data_profiler.py --file data.csv
    python3 data_profiler.py --file data.csv --columns col1,col2
    python3 data_profiler.py --file data.csv --format json
    python3 data_profiler.py --file data.csv --monitor
"""

import argparse
import csv
import json
import math
import sys
from collections import Counter, defaultdict

__all__ = ['Counter', 'annotations', 'argparse', 'csv', 'defaultdict', 'json', 'math', 'sys']
