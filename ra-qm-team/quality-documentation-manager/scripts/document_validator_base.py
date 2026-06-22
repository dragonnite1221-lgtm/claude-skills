# ruff: noqa: F403, F405, E501
"""
Document Validator - Quality Documentation Compliance Checker

Validates document metadata, numbering conventions, and control requirements
for ISO 13485 and 21 CFR Part 11 compliance.

Usage:
    python document_validator.py --doc document.json
    python document_validator.py --interactive
    python document_validator.py --doc document.json --output json
"""
import argparse
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from enum import Enum


# fmt: off
__all__ = ['Dict', 'Enum', 'List', 'Optional', 'Tuple', 'argparse', 'asdict', 'dataclass', 'datetime', 'field', 'json', 're', 'sys', 'timedelta']  # noqa: E501
# fmt: on
