# ruff: noqa: F403, F405, E501
"""
Management Review Tracker - QMS Management Review Preparation and Tracking

Tracks management review inputs, action items, and generates review reports
for ISO 13485 compliance.

Usage:
    python management_review_tracker.py --data review_data.json
    python management_review_tracker.py --interactive
    python management_review_tracker.py --data review_data.json --output json
"""
import argparse
import json
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from enum import Enum


# fmt: off
__all__ = ['Dict', 'Enum', 'List', 'Optional', 'argparse', 'asdict', 'dataclass', 'datetime', 'field', 'json', 'sys', 'timedelta']  # noqa: E501
# fmt: on
