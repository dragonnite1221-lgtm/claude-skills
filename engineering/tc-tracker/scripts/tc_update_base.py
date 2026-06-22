# ruff: noqa: E501
#!/usr/bin/env python3
"""TC Update — Update an existing TC record.

Each invocation appends a sequential R<n> revision entry, refreshes the
`updated` timestamp, validates the resulting record, and writes atomically.

Usage:
    # Status transition (validated against state machine)
    python3 tc_update.py --root . --tc-id <TC-ID> \\
        --set-status in_progress --reason "Starting implementation"

    # Add files
    python3 tc_update.py --root . --tc-id <TC-ID> \\
        --add-file src/auth.py:created \\
        --add-file src/middleware.py:modified

    # Add a test case
    python3 tc_update.py --root . --tc-id <TC-ID> \\
        --add-test "Login returns JWT" \\
        --test-procedure "POST /login with valid creds" \\
        --test-expected "200 + token in body"

    # Append handoff data
    python3 tc_update.py --root . --tc-id <TC-ID> \\
        --handoff-progress "JWT middleware wired up" \\
        --handoff-next "Write integration tests" \\
        --handoff-next "Update README" \\
        --handoff-blocker "Waiting on test fixtures"

    # Append a freeform note
    python3 tc_update.py --root . --tc-id <TC-ID> --note "Decision: use HS256"

Exit codes:
    0 = updated
    1 = warnings (e.g. validation produced errors but write skipped)
    2 = critical error (file missing, invalid transition, parse error)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

__all__ = ['Path', 'annotations', 'argparse', 'datetime', 'json', 're', 'sys', 'timezone']
