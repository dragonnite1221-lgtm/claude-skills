# ruff: noqa: F403, F405, E501
"""
Dependency Scanner - Multi-language dependency vulnerability and analysis tool.

This script parses dependency files from various package managers, extracts direct
and transitive dependencies, checks against built-in vulnerability databases,
and provides comprehensive security analysis with actionable recommendations.

Author: Claude Skills Engineering Team
License: MIT
"""
import json
import os
import re
import sys
import argparse
from typing import Dict, List, Set, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib
import subprocess


# fmt: off
__all__ = ['Any', 'Dict', 'List', 'Optional', 'Path', 'Set', 'Tuple', 'argparse', 'asdict', 'dataclass', 'datetime', 'hashlib', 'json', 'os', 're', 'subprocess', 'sys']  # noqa: E501
# fmt: on
