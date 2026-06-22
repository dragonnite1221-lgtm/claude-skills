# ruff: noqa: E501
#!/usr/bin/env python3
"""
Workflow Validator

Validates Jira workflow definitions (JSON input) for anti-patterns and common
issues. Checks for dead-end states, orphan states, missing transitions, circular
paths, and produces a health score with severity-rated findings.

Usage:
    python workflow_validator.py workflow.json
    python workflow_validator.py workflow.json --format json
"""

import argparse
import json
import sys
from typing import Any, Dict, List, Optional, Set, Tuple


# ---------------------------------------------------------------------------
# Validation Configuration
# ---------------------------------------------------------------------------

__all__ = ['Any', 'Dict', 'List', 'Optional', 'Set', 'Tuple', 'argparse', 'json', 'sys']
