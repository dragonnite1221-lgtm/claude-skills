# ruff: noqa: E501
#!/usr/bin/env python3
"""
SOC 2 Control Matrix Builder

Generates a SOC 2 control matrix from selected Trust Service Criteria categories.
Outputs in markdown, JSON, or CSV format.

Usage:
    python control_matrix_builder.py --categories security --format md
    python control_matrix_builder.py --categories security,availability --format json
    python control_matrix_builder.py --categories security,availability,confidentiality,processing-integrity,privacy --format csv
"""

import argparse
import csv
import io
import json
import sys
from typing import Dict, List, Any


# Trust Service Criteria control definitions

__all__ = ['Any', 'Dict', 'List', 'argparse', 'csv', 'io', 'json', 'sys']
