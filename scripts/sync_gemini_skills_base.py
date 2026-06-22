# ruff: noqa: E501
#!/usr/bin/env python3
"""
Sync Gemini Skills - Generate symlinks and index for Gemini CLI compatibility.

This script scans the skill domains for SKILL.md files and creates:
1. Symlinks in .gemini/skills/ directory
2. skills-index.json manifest for tooling

Usage:
    python scripts/sync-gemini-skills.py [--dry-run] [--verbose]
"""

import argparse
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Optional

__all__ = ['Dict', 'List', 'Optional', 'Path', 'argparse', 'json', 'os', 'shutil', 'sys']
