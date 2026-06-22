# ruff: noqa: E501
#!/usr/bin/env python3
"""
Spec Generator - Generates a feature specification template from a name and description.

Produces a complete spec document with all required sections pre-filled with
guidance prompts. Output can be markdown or structured JSON.

No external dependencies - uses only Python standard library.
"""

import argparse
import json
import sys
import textwrap
from datetime import date
from pathlib import Path
from typing import Dict, Any, Optional

__all__ = ['Any', 'Dict', 'Optional', 'Path', 'argparse', 'date', 'json', 'sys', 'textwrap']
