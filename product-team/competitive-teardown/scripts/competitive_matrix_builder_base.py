# ruff: noqa: E501
#!/usr/bin/env python3
"""Competitive Matrix Builder — Analyze and score competitors across feature dimensions.

Generates weighted competitive matrices, gap analysis, and positioning insights
from structured competitor data.

Usage:
    python competitive_matrix_builder.py competitors.json --format json
    python competitive_matrix_builder.py competitors.json --format text
    python competitive_matrix_builder.py competitors.json --format text --weights pricing=2,ux=1.5
"""

import argparse
import json
import sys
from typing import Dict, List, Any, Optional
from datetime import datetime
from statistics import mean, stdev

__all__ = ['Any', 'Dict', 'List', 'Optional', 'argparse', 'datetime', 'json', 'mean', 'stdev', 'sys']
