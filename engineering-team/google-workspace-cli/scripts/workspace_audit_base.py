# ruff: noqa: E501
#!/usr/bin/env python3
"""
Google Workspace Security Audit — Audit Workspace configuration for security risks.

Checks Drive external sharing, Gmail forwarding rules, OAuth app grants,
Calendar visibility, admin settings, and generates remediation commands.
Runs in demo mode with embedded sample data when gws is not installed.

Usage:
    python3 workspace_audit.py
    python3 workspace_audit.py --json
    python3 workspace_audit.py --services gmail,drive,calendar
    python3 workspace_audit.py --demo
"""

import argparse
import json
import shutil
import subprocess
import sys
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional

__all__ = ['Dict', 'List', 'Optional', 'argparse', 'asdict', 'dataclass', 'field', 'json', 'shutil', 'subprocess', 'sys']
