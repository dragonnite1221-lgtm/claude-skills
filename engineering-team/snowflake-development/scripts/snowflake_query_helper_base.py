# ruff: noqa: E501
#!/usr/bin/env python3
"""
Snowflake Query Helper

Generate common Snowflake SQL patterns: MERGE upserts, Dynamic Table DDL,
and RBAC grant statements. Outputs ready-to-use SQL that follows Snowflake
best practices.

Usage:
    python snowflake_query_helper.py merge --target customers --source stg_customers --key id --columns name,email
    python snowflake_query_helper.py dynamic-table --name cleaned_events --warehouse transform_wh --lag "5 minutes"
    python snowflake_query_helper.py grant --role analyst --database analytics --schemas public --privileges SELECT,USAGE
    python snowflake_query_helper.py merge --target t --source s --key id --columns a,b --json
"""

import argparse
import json
import sys
import textwrap
from typing import List, Optional

__all__ = ['List', 'Optional', 'argparse', 'json', 'sys', 'textwrap']
