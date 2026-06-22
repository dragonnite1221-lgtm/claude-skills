# ruff: noqa: E501
#!/usr/bin/env python3
"""AgentHub session state machine and lifecycle manager.

Manages session states (init → running → evaluating → merged/archived),
lists sessions, and handles cleanup of worktrees and branches.

Usage:
    python session_manager.py --list
    python session_manager.py --status 20260317-143022
    python session_manager.py --update 20260317-143022 --state running
    python session_manager.py --cleanup 20260317-143022
    python session_manager.py --demo
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

__all__ = ['argparse', 'datetime', 'json', 'os', 'subprocess', 'sys', 'timezone']
