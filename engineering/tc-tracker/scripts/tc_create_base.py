# ruff: noqa: E501
#!/usr/bin/env python3
"""TC Create — Create a new Technical Change record.

Generates the next sequential TC ID, scaffolds the record directory, writes a
fully populated tc_record.json (status=planned, R1 creation revision), and
appends a registry entry with recomputed statistics.

Usage:
    python3 tc_create.py --root . --name user-auth \\
        --title "Add JWT authentication" --scope feature --priority high \\
        --summary "Adds JWT login + middleware" \\
        --motivation "Required for protected endpoints"

Exit codes:
    0 = created
    1 = warnings (e.g. validation soft warnings)
    2 = critical error (registry missing, bad args, schema invalid)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

__all__ = ['Path', 'annotations', 'argparse', 'datetime', 'json', 'os', 're', 'sys', 'timezone']
