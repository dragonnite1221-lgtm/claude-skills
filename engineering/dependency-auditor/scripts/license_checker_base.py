# ruff: noqa: F403, F405, E501
"""
License Checker - Dependency license compliance and conflict analysis tool.

This script analyzes dependency licenses from package metadata, classifies them
into risk categories, detects license conflicts, and generates compliance
reports with actionable recommendations for legal risk management.

Author: Claude Skills Engineering Team
License: MIT
"""
import json
import os
import sys
import argparse
from typing import Dict, List, Set, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime
import re
from enum import Enum


# fmt: off
__all__ = ['Any', 'Dict', 'Enum', 'List', 'Optional', 'Path', 'Set', 'Tuple', 'argparse', 'asdict', 'dataclass', 'datetime', 'json', 'os', 're', 'sys']  # noqa: E501
# fmt: on
