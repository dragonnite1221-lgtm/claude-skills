# ruff: noqa: E501
#!/usr/bin/env python3
"""
validate_project.py — Validate a generated project directory for common issues.

Checks:
  - README.md exists and is non-empty
  - .gitignore exists
  - .env.example exists (if code references env vars)
  - Package manifest exists (package.json, requirements.txt, go.mod, etc.)
  - No .env file committed (secrets leak)
  - At least one test file exists
  - No TODO/FIXME placeholders in generated code

Usage:
    python3 validate_project.py /path/to/project
    python3 validate_project.py /path/to/project --format json
    python3 validate_project.py /path/to/project --strict
"""

import argparse
import json
import os
import re
import sys

__all__ = ['argparse', 'json', 'os', 're', 'sys']
