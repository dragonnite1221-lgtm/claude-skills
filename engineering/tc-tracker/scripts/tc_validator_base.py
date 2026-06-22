# ruff: noqa: E501
#!/usr/bin/env python3
"""TC Validator — Validate a TC record or registry against the schema and state machine.

Enforces:
  * Schema shape (required fields, types, enum values)
  * State machine transitions (planned -> in_progress -> implemented -> tested -> deployed)
  * Sequential R<n> revision IDs and T<n> test IDs
  * TC ID format (TC-NNN-MM-DD-YY-slug)
  * Sub-TC ID format (TC-NNN.A or TC-NNN.A.N)
  * Approval consistency (approved=true requires approved_by + approved_date)

Usage:
    python3 tc_validator.py --record path/to/tc_record.json
    python3 tc_validator.py --registry path/to/tc_registry.json
    python3 tc_validator.py --record path/to/tc_record.json --json

Exit codes:
    0 = valid
    1 = validation errors
    2 = file not found / JSON parse error / bad CLI args
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

__all__ = ['Path', 'annotations', 'argparse', 'datetime', 'json', 're', 'sys']
