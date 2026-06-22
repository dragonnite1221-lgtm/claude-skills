# ruff: noqa: E501
#!/usr/bin/env python3
"""
Secret Scanner

Detects hardcoded secrets, API keys, and credentials in source code.
Identifies exposed secrets before they reach version control.

Usage:
    python secret_scanner.py /path/to/project
    python secret_scanner.py /path/to/file.py
    python secret_scanner.py /path/to/project --format json
    python secret_scanner.py --list-patterns
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional
from enum import Enum

__all__ = ['Dict', 'Enum', 'List', 'Optional', 'Path', 'argparse', 'dataclass', 'json', 'os', 're', 'sys']
