# ruff: noqa: E501
#!/usr/bin/env python3
"""Dry-run validation for the AgentHub plugin.

Checks JSON validity, YAML frontmatter, markdown structure, cross-file
consistency, script --help, and referenced file existence — without
creating any sessions or worktrees.

Usage:
    python dry_run.py                # Run all checks
    python dry_run.py --verbose      # Show per-file details
    python dry_run.py --help
"""

import argparse
import json
import os
import re
import subprocess
import sys

__all__ = ['argparse', 'json', 'os', 're', 'subprocess', 'sys']
