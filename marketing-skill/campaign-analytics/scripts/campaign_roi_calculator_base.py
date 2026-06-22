# ruff: noqa: E501
#!/usr/bin/env python3
"""
Campaign ROI Calculator - Comprehensive campaign ROI and performance metrics.

Calculates:
  - ROI (Return on Investment)
  - ROAS (Return on Ad Spend)
  - CPA (Cost per Acquisition/Customer)
  - CPL (Cost per Lead)
  - CAC (Customer Acquisition Cost)
  - CTR (Click-Through Rate)
  - CVR (Conversion Rate - Leads to Customers)

Includes industry benchmarking and underperformance flagging.

Usage:
    python campaign_roi_calculator.py campaign_data.json
    python campaign_roi_calculator.py campaign_data.json --format json
"""

import argparse
import json
import sys
from typing import Any, Dict, List, Optional


# Industry benchmark ranges by channel
# Format: {metric: {channel: (low, target, high)}}

__all__ = ['Any', 'Dict', 'List', 'Optional', 'argparse', 'json', 'sys']
