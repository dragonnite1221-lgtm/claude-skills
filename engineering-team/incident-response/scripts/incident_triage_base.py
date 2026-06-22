# ruff: noqa: E501
#!/usr/bin/env python3
"""
incident_triage.py — Incident Classification, Triage, and Escalation

Classifies security events into 14 incident types, applies false-positive
filters, scores severity (SEV1-SEV4), determines escalation path, and
performs forensic pre-analysis for confirmed incidents.

Usage:
    echo '{"event_type": "ransomware", "raw_payload": {...}}' | python3 incident_triage.py
    python3 incident_triage.py --input event.json --json
    python3 incident_triage.py --classify --false-positive-check --input event.json --json

Exit codes:
    0  SEV3/SEV4 or clean — standard handling
    1  SEV2 — elevated response required
    2  SEV1 — critical incident declared
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Constants — Forensic Pre-Analysis Base (reused from pre_analysis.py logic)
# ---------------------------------------------------------------------------

__all__ = ['Any', 'Dict', 'List', 'Optional', 'Tuple', 'argparse', 'datetime', 'json', 'sys', 'timezone']
