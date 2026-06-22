# ruff: noqa: E501
#!/usr/bin/env python3
"""
Sync Codex Skills - Generate symlinks and index for OpenAI Codex compatibility.

This script scans all domain folders for SKILL.md files and creates:
1. Symlinks in .codex/skills/ directory
2. skills-index.json manifest for tooling

Usage:
    python scripts/sync-codex-skills.py [--dry-run] [--verbose]
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional


# Skill domain configuration

__all__ = ['Dict', 'List', 'Optional', 'Path', 'argparse', 'json', 'os', 'sys']
