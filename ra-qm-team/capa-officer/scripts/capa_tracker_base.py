# ruff: noqa: F403, F405, E501
"""
CAPA Tracker - Corrective and Preventive Action Management Tool

Tracks CAPA status, calculates metrics, identifies overdue items,
and generates reports for management review.

Usage:
    python capa_tracker.py --capas capas.json
    python capa_tracker.py --interactive
    python capa_tracker.py --capas capas.json --output json
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
