# ruff: noqa: F403, F405, E501
"""
Tech Debt Scanner

Scans a codebase directory for tech debt signals using AST parsing (Python) and 
regex patterns (any language). Detects various forms of technical debt and generates
both JSON inventory and human-readable reports.

Usage:
    python debt_scanner.py /path/to/codebase
    python debt_scanner.py /path/to/codebase --config config.json
    python debt_scanner.py /path/to/codebase --output report.json --format both
"""
import ast
import json
import argparse
import os
import re
import sys
from collections import defaultdict, Counter
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple


# fmt: off
__all__ = ['Any', 'Counter', 'Dict', 'List', 'Optional', 'Path', 'Set', 'Tuple', 'argparse', 'ast', 'datetime', 'defaultdict', 'json', 'os', 're', 'sys']  # noqa: E501
# fmt: on
