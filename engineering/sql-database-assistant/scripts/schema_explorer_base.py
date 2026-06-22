# ruff: noqa: E501
#!/usr/bin/env python3
"""
Schema Explorer

Generates schema documentation from database introspection queries.
Outputs the introspection SQL and sample documentation templates
for PostgreSQL, MySQL, SQLite, and SQL Server.

Since this tool runs without a live database connection, it generates:
1. The introspection queries you need to run
2. Documentation templates from the results
3. Sample schema docs for common table patterns

Usage:
    python schema_explorer.py --dialect postgres --tables all --format md
    python schema_explorer.py --dialect mysql --tables users,orders --format json
    python schema_explorer.py --dialect sqlite --tables all --json
"""

import argparse
import json
import sys
import textwrap
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict


# ---------------------------------------------------------------------------
# Introspection query templates per dialect
# ---------------------------------------------------------------------------

__all__ = ['Dict', 'List', 'Optional', 'argparse', 'asdict', 'dataclass', 'json', 'sys', 'textwrap']
