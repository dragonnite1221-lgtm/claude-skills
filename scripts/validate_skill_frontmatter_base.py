# ruff: noqa: E501
#!/usr/bin/env python3
"""Validate SKILL.md frontmatter and Gemini mirror consistency."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

__all__ = ['Any', 'Path', 'annotations', 'argparse', 'asdict', 'dataclass', 'importlib', 'json', 'os', 're', 'sys']
