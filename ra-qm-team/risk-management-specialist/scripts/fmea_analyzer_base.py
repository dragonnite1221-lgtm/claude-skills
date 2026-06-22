# ruff: noqa: E501
#!/usr/bin/env python3
"""
FMEA Analyzer - Failure Mode and Effects Analysis for medical device risk management.

Supports Design FMEA (dFMEA) and Process FMEA (pFMEA) per ISO 14971 and IEC 60812.
Calculates Risk Priority Numbers (RPN), identifies critical items, and generates
risk reduction recommendations.

Usage:
    python fmea_analyzer.py --data fmea_input.json
    python fmea_analyzer.py --interactive
    python fmea_analyzer.py --data fmea_input.json --output json
"""

import argparse
import json
import sys
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Tuple
from enum import Enum
from datetime import datetime

__all__ = ['Dict', 'Enum', 'List', 'Optional', 'Tuple', 'argparse', 'asdict', 'dataclass', 'datetime', 'field', 'json', 'sys']
