# ruff: noqa: E501
#!/usr/bin/env python3
"""
complexity_checker.py — Detect over-engineering in Python/TypeScript files.

Karpathy Principle #2 (Simplicity First): "No abstractions for single-use code.
If you write 200 lines and it could be 50, rewrite it."

Checks:
  - Cyclomatic complexity (branches per function)
  - Class count relative to file size (too many classes = premature abstraction)
  - Nesting depth (deep nesting = hard to read)
  - Function length (long functions = doing too much)
  - Import count (many imports = over-coupled)
  - Abstract base classes / protocols for small files (premature patterns)

Usage:
    python complexity_checker.py path/to/file.py
    python complexity_checker.py src/ --threshold medium
    python complexity_checker.py . --ext py,ts --json

Thresholds:
    strict  — flags aggressively (good for new code)
    medium  — balanced (default)
    relaxed — flags only egregious cases (good for legacy code)
"""
from __future__ import annotations
import argparse
import json
import os
import re
import sys
from pathlib import Path

# --- Thresholds ---

__all__ = ['Path', 'annotations', 'argparse', 'json', 'os', 're', 'sys']
