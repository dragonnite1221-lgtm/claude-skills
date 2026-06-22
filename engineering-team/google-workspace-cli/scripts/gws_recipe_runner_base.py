# ruff: noqa: E501
#!/usr/bin/env python3
"""
Google Workspace CLI Recipe Runner — Catalog, search, and execute gws recipes.

Browse 43 built-in recipes, filter by persona, search by keyword,
and run with dry-run support.

Usage:
    python3 gws_recipe_runner.py --list
    python3 gws_recipe_runner.py --search "email"
    python3 gws_recipe_runner.py --describe standup-report
    python3 gws_recipe_runner.py --run standup-report --dry-run
    python3 gws_recipe_runner.py --persona pm --list
    python3 gws_recipe_runner.py --list --json
"""

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional

__all__ = ['Dict', 'List', 'Optional', 'argparse', 'asdict', 'dataclass', 'field', 'json', 'subprocess', 'sys']
