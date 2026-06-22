# ruff: noqa: F403, F405, E501
"""
Budget Variance Analyzer

Analyzes actual vs budget vs prior year performance with materiality
threshold filtering, favorable/unfavorable classification, and
department/category breakdown.

Usage:
    python budget_variance_analyzer.py budget_data.json
    python budget_variance_analyzer.py budget_data.json --format json
    python budget_variance_analyzer.py budget_data.json --threshold-pct 5 --threshold-amt 25000
"""
import argparse
import json
import sys
from typing import Any, Dict, List, Optional, Tuple


# fmt: off
__all__ = ['Any', 'Dict', 'List', 'Optional', 'Tuple', 'argparse', 'json', 'sys']  # noqa: E501
# fmt: on
