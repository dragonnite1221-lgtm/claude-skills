# ruff: noqa: F403, F405, E501
"""
PIR (Post-Incident Review) Generator

Generates comprehensive Post-Incident Review documents from incident data, timelines,
and actions taken. Applies multiple RCA frameworks including 5 Whys, Fishbone diagram,
and Timeline analysis.

This tool creates structured PIR documents with root cause analysis, lessons learned,
action items, and follow-up recommendations.

Usage:
    python pir_generator.py --incident incident.json --timeline timeline.json --output pir.md
    python pir_generator.py --incident incident.json --rca-method fishbone --action-items
    cat incident.json | python pir_generator.py --format markdown
"""
import argparse
import json
import sys
import re
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict, Counter


# fmt: off
__all__ = ['Any', 'Counter', 'Dict', 'List', 'Optional', 'Tuple', 'argparse', 'datetime', 'defaultdict', 'json', 're', 'sys', 'timedelta', 'timezone']  # noqa: E501
# fmt: on
