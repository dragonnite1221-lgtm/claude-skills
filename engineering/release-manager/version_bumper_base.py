# ruff: noqa: F403, F405, E501
"""
Version Bumper

Analyzes commits since last tag to determine the correct version bump (major/minor/patch) 
based on conventional commits. Handles pre-release versions (alpha, beta, rc) and generates 
version bump commands for various package files.

Input: current version + commit list JSON or git log
Output: recommended new version + bump commands + updated file snippets
"""
import argparse
import json
import re
import sys
from typing import Dict, List, Optional, Tuple, Union
from enum import Enum
from dataclasses import dataclass


# fmt: off
__all__ = ['Dict', 'Enum', 'List', 'Optional', 'Tuple', 'Union', 'argparse', 'dataclass', 'json', 're', 'sys']  # noqa: E501
# fmt: on
