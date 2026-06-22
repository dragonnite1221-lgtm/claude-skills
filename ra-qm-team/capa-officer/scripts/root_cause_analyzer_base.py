# ruff: noqa: F403, F405, E501
"""
Root Cause Analyzer - Structured root cause analysis for CAPA investigations.

Supports multiple analysis methodologies:
- 5-Why Analysis
- Fishbone (Ishikawa) Diagram
- Fault Tree Analysis
- Kepner-Tregoe Problem Analysis

Generates structured root cause reports and CAPA recommendations.

Usage:
    python root_cause_analyzer.py --method 5why --problem "High defect rate in assembly line"
    python root_cause_analyzer.py --interactive
    python root_cause_analyzer.py --data investigation.json --output json
"""
import argparse
import json
import sys
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional
from enum import Enum
from datetime import datetime


# fmt: off
__all__ = ['Dict', 'Enum', 'List', 'Optional', 'argparse', 'asdict', 'dataclass', 'datetime', 'field', 'json', 'sys']  # noqa: E501
# fmt: on
