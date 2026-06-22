# ruff: noqa: E501
#!/usr/bin/env python3
"""
autoresearch-agent: Results Viewer

View experiment results in multiple formats: terminal, CSV, Markdown.
Supports single experiment, domain, or cross-experiment dashboard.

Usage:
    python scripts/log_results.py --experiment engineering/api-speed
    python scripts/log_results.py --domain engineering
    python scripts/log_results.py --dashboard
    python scripts/log_results.py --experiment engineering/api-speed --format csv --output results.csv
    python scripts/log_results.py --experiment engineering/api-speed --format markdown --output results.md
    python scripts/log_results.py --dashboard --format markdown --output dashboard.md
"""

import argparse
import csv
import io
import sys
import time
from pathlib import Path

__all__ = ['Path', 'argparse', 'csv', 'io', 'sys', 'time']
