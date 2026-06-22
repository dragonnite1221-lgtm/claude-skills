# ruff: noqa: E501
#!/usr/bin/env python3
"""
helm-chart-builder: Chart Analyzer

Static analysis of Helm chart directories for structural issues, template
anti-patterns, missing labels, hardcoded values, and security baseline checks.

Usage:
    python scripts/chart_analyzer.py mychart/
    python scripts/chart_analyzer.py mychart/ --output json
    python scripts/chart_analyzer.py mychart/ --security
"""

import argparse
import json
import re
import sys
from pathlib import Path


# --- Analysis Rules ---

__all__ = ['Path', 'argparse', 'json', 're', 'sys']
