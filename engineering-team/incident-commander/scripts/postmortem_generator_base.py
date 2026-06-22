# ruff: noqa: E501
#!/usr/bin/env python3
"""
Postmortem Generator - Generate structured postmortem reports with 5-Whys analysis.

Produces comprehensive incident postmortem documents from structured JSON input,
including root cause analysis, contributing factor classification, action item
validation, MTTD/MTTR metrics, and customer impact summaries.

Usage:
    python postmortem_generator.py incident_data.json
    python postmortem_generator.py incident_data.json --format markdown
    python postmortem_generator.py incident_data.json --format json
    cat incident_data.json | python postmortem_generator.py

Input:
    JSON object with keys: incident, timeline, resolution, action_items, participants.
    See SKILL.md for the full input schema.
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple


# ---------- Constants and Configuration ----------

__all__ = ['Any', 'Dict', 'List', 'Optional', 'Tuple', 'argparse', 'datetime', 'json', 'sys', 'timezone']
