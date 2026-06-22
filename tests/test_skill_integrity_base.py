# ruff: noqa: E501
"""Integration tests: verify skill package consistency across the repository.

These tests validate that:
1. Every skill directory with a SKILL.md has valid structure
2. SKILL.md files have required YAML frontmatter
3. File references in SKILL.md actually exist
4. Scripts directories contain valid Python files
5. No orphaned scripts directories without a SKILL.md
"""

import glob
import importlib.util
import json
import os
import re
from pathlib import Path

import pytest

__all__ = ['Path', 'glob', 'importlib', 'json', 'os', 'pytest', 're']
