# ruff: noqa: E501
#!/usr/bin/env python3
"""
Funnel Analyzer - Conversion funnel analysis with bottleneck detection.

Analyzes marketing/sales funnels to identify:
  - Stage-to-stage conversion rates and drop-off percentages
  - Biggest bottleneck (largest absolute and relative drops)
  - Overall funnel conversion rate
  - Segment comparison when multiple segments are provided

Usage:
    python funnel_analyzer.py funnel_data.json
    python funnel_analyzer.py funnel_data.json --format json
"""

import argparse
import json
import sys
from typing import Any, Dict, List, Optional

__all__ = ['Any', 'Dict', 'List', 'Optional', 'argparse', 'json', 'sys']
