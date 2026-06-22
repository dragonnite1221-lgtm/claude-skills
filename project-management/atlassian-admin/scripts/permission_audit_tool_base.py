# ruff: noqa: E501
#!/usr/bin/env python3
"""
Permission Audit Tool

Analyzes Atlassian permission schemes for security issues. Checks for
over-permissioned groups, direct user permissions, missing restrictions on
sensitive actions, inconsistencies across projects, and compliance gaps.

Usage:
    python permission_audit_tool.py permissions.json
    python permission_audit_tool.py permissions.json --format json
"""

import argparse
import json
import sys
from typing import Any, Dict, List, Optional, Set


# ---------------------------------------------------------------------------
# Audit Configuration
# ---------------------------------------------------------------------------

__all__ = ['Any', 'Dict', 'List', 'Optional', 'Set', 'argparse', 'json', 'sys']
