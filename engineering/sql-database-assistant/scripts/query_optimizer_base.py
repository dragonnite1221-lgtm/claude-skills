# ruff: noqa: E501
#!/usr/bin/env python3
"""
SQL Query Optimizer — Static Analysis

Analyzes SQL queries for common performance issues:
- SELECT * usage
- Missing WHERE clauses on UPDATE/DELETE
- Cartesian joins (missing JOIN conditions)
- Subqueries in SELECT list
- Missing LIMIT on unbounded SELECTs
- Function calls on indexed columns (non-sargable)
- LIKE with leading wildcard
- ORDER BY RAND()
- UNION instead of UNION ALL
- NOT IN with subquery (NULL-unsafe)

Usage:
    python query_optimizer.py --query "SELECT * FROM users"
    python query_optimizer.py --query queries.sql --dialect postgres
    python query_optimizer.py --query "SELECT * FROM orders" --json
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, asdict
from typing import List, Optional

__all__ = ['List', 'Optional', 'argparse', 'asdict', 'dataclass', 'json', 'os', 're', 'sys']
