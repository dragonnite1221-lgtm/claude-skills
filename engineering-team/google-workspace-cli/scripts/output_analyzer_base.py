# ruff: noqa: E501
#!/usr/bin/env python3
"""
Google Workspace CLI Output Analyzer — Parse, filter, and aggregate JSON/NDJSON output.

Reads JSON arrays or NDJSON streams from stdin or file, applies filters,
projections, sorting, grouping, and outputs in table/csv/json format.

Usage:
    gws drive files list --json | python3 output_analyzer.py --count
    gws drive files list --json | python3 output_analyzer.py --filter "mimeType=application/pdf"
    gws drive files list --json | python3 output_analyzer.py --select "name,size" --format table
    python3 output_analyzer.py --input results.json --group-by "mimeType"
    python3 output_analyzer.py --demo --select "name,mimeType,size" --format table
"""

import argparse
import csv
import io
import json
import sys
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

__all__ = ['Any', 'Dict', 'List', 'Optional', 'argparse', 'csv', 'dataclass', 'io', 'json', 'sys']
