# ruff: noqa: F403, F405, E501
"""
Quality Scorer - Scores skills across multiple quality dimensions

This script provides comprehensive quality assessment for skills in the claude-skills
ecosystem by evaluating documentation, code quality, completeness, security, and usability.
Generates letter grades, tier recommendations, and improvement roadmaps.

Usage:
    python quality_scorer.py <skill_path> [--detailed] [--minimum-score SCORE] [--json]

Author: Claude Skills Engineering Team
Version: 2.0.0
Dependencies: Python Standard Library Only
Changelog:
  v2.0.0 - Added Security dimension (opt-in via --include-security flag)
           Default: 4 dimensions × 25% (backward compatible)
           With --include-security: 5 dimensions × 20%
  v1.0.0 - Initial release with 4 dimensions (25% each)
"""
import argparse
import ast
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from security_scorer import SecurityScorer


# fmt: off
__all__ = ['Any', 'Dict', 'List', 'Optional', 'Path', 'SecurityScorer', 'Tuple', 'argparse', 'ast', 'datetime', 'json', 'os', 're', 'sys']  # noqa: E501
# fmt: on
