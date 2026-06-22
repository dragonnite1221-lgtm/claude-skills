# ruff: noqa: E501
#!/usr/bin/env python3
"""Analyze Vault or cloud secret manager audit logs for anomalies.

Reads JSON-lines or JSON-array audit log files and flags unusual access
patterns including volume spikes, off-hours access, new source IPs,
and failed authentication attempts.

Usage:
    python audit_log_analyzer.py --log-file vault-audit.log --threshold 5
    python audit_log_analyzer.py --log-file audit.json --threshold 3 --json

Expected log entry format (JSON lines or JSON array):
{
  "timestamp": "2026-03-20T14:32:00Z",
  "type": "request",
  "auth": {"accessor": "token-abc123", "entity_id": "eid-001", "display_name": "approle-payment-svc"},
  "request": {"path": "secret/data/production/payment/api-keys", "operation": "read"},
  "response": {"status_code": 200},
  "remote_address": "10.0.1.15"
}

Fields are optional — the analyzer works with whatever is available.
"""

import argparse
import json
import sys
import textwrap
from collections import defaultdict
from datetime import datetime

__all__ = ['argparse', 'datetime', 'defaultdict', 'json', 'sys', 'textwrap']
