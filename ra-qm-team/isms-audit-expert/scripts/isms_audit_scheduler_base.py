# ruff: noqa: E501
#!/usr/bin/env python3
"""
ISMS Audit Scheduler

Risk-based audit planning and scheduling for ISO 27001 compliance.
Generates annual audit plans based on control risk ratings.

Usage:
    python isms_audit_scheduler.py --year 2025 --output audit_plan.json
    python isms_audit_scheduler.py --controls controls.csv --format markdown
"""

import argparse
import csv
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional


# ISO 27001:2022 Annex A control domains

__all__ = ['Any', 'Dict', 'List', 'Optional', 'argparse', 'csv', 'datetime', 'json', 'sys', 'timedelta']
