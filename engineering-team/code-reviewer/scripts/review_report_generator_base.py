# ruff: noqa: E501
#!/usr/bin/env python3
"""
Review Report Generator

Generates comprehensive code review reports by combining PR analysis
and code quality findings into structured, actionable reports.

Usage:
    python review_report_generator.py /path/to/repo
    python review_report_generator.py . --pr-analysis pr_results.json --quality-analysis quality_results.json
    python review_report_generator.py /path/to/repo --format markdown --output review.md
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# Severity weights for prioritization

__all__ = ['Dict', 'List', 'Optional', 'Path', 'Tuple', 'argparse', 'datetime', 'json', 'os', 'subprocess', 'sys']
