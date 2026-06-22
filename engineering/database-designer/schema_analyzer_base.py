# ruff: noqa: F403, F405, E501
"""
Database Schema Analyzer

Analyzes SQL DDL statements and JSON schema definitions for:
- Normalization level compliance (1NF-BCNF)
- Missing constraints (FK, NOT NULL, UNIQUE)
- Data type issues and antipatterns
- Naming convention violations
- Missing indexes on foreign key columns
- Table relationship mapping
- Generates Mermaid ERD diagrams

Input: SQL DDL file or JSON schema definition
Output: Analysis report + Mermaid ERD + recommendations

Usage:
    python schema_analyzer.py --input schema.sql --output-format json
    python schema_analyzer.py --input schema.json --output-format text
    python schema_analyzer.py --input schema.sql --generate-erd --output analysis.json
"""
import argparse
import json
import re
import sys
from collections import defaultdict, namedtuple
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass, asdict


# fmt: off
__all__ = ['Any', 'Dict', 'List', 'Optional', 'Set', 'Tuple', 'argparse', 'asdict', 'dataclass', 'defaultdict', 'json', 'namedtuple', 're', 'sys']  # noqa: E501
# fmt: on
