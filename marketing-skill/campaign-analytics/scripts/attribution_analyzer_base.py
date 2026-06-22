# ruff: noqa: E501
#!/usr/bin/env python3
"""
Attribution Analyzer - Multi-touch attribution modeling for marketing campaigns.

Implements 5 attribution models:
  - first-touch: 100% credit to first interaction
  - last-touch: 100% credit to last interaction
  - linear: Equal credit across all touchpoints
  - time-decay: Exponential decay favoring recent touchpoints
  - position-based: 40% first, 40% last, 20% split among middle

Usage:
    python attribution_analyzer.py data.json
    python attribution_analyzer.py data.json --model time-decay
    python attribution_analyzer.py data.json --model time-decay --half-life 14
    python attribution_analyzer.py data.json --format json
"""

import argparse
import json
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

__all__ = ['Any', 'Dict', 'List', 'Optional', 'argparse', 'datetime', 'json', 'sys']
