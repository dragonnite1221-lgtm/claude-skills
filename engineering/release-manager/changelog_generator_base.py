# ruff: noqa: F403, F405, E501
"""
Changelog Generator

Parses git log output in conventional commits format and generates structured changelogs
in multiple formats (Markdown, Keep a Changelog). Groups commits by type, extracts scope,
links to PRs/issues, and highlights breaking changes.

Input: git log text (piped from git log) or JSON array of commits
Output: formatted CHANGELOG.md section + release summary stats
"""
import argparse
import json
import re
import sys
from collections import defaultdict, Counter
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union


# fmt: off
__all__ = ['Counter', 'Dict', 'List', 'Optional', 'Tuple', 'Union', 'argparse', 'datetime', 'defaultdict', 'json', 're', 'sys']  # noqa: E501
# fmt: on
