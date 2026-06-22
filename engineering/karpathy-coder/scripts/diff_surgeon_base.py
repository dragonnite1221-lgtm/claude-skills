# ruff: noqa: E501
#!/usr/bin/env python3
"""
diff_surgeon.py — Detect diff noise: changes that don't trace to the stated goal.

Karpathy Principle #3 (Surgical Changes): "Every changed line should trace
directly to the user's request."

Analyzes a git diff and flags:
  - Comment-only changes (unrelated to the task)
  - Whitespace / formatting changes
  - Import additions not used by the new code
  - Style changes (quote style, trailing commas, semicolons)
  - Docstring additions to unchanged functions
  - Variable renames in untouched code
  - Type annotation additions to unchanged signatures

Usage:
    python diff_surgeon.py                          # analyze staged diff
    python diff_surgeon.py --diff HEAD~1..HEAD      # analyze last commit
    python diff_surgeon.py --file changes.diff      # analyze a diff file
    python diff_surgeon.py --json

Exit codes:
    0  clean — all changes look intentional
    1  noise detected — review before committing
"""
from __future__ import annotations
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

# --- Noise detectors ---

__all__ = ['Path', 'annotations', 'argparse', 'json', 're', 'subprocess', 'sys']
