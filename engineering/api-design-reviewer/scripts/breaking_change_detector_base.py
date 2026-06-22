# ruff: noqa: F403, F405, E501
"""
Breaking Change Detector - Compares API specification versions to identify breaking changes.

This script analyzes two versions of an API specification and detects potentially
breaking changes including:
- Removed endpoints
- Modified response structures
- Removed or renamed fields
- Field type changes
- New required fields
- HTTP status code changes
- Parameter changes

Generates detailed reports with migration guides for each breaking change.
"""
import argparse
import json
import sys
from typing import Any, Dict, List, Set, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum


# fmt: off
__all__ = ['Any', 'Dict', 'Enum', 'List', 'Optional', 'Set', 'Tuple', 'Union', 'argparse', 'dataclass', 'field', 'json', 'sys']  # noqa: E501
# fmt: on
