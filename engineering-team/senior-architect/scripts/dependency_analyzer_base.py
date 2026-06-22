# ruff: noqa: F403, F405, E501
"""
Dependency Analyzer

Analyzes project dependencies for:
- Dependency tree (direct and transitive)
- Circular dependencies between modules
- Coupling score (0-100)
- Outdated packages (basic detection)

Supports:
- npm/yarn (package.json)
- Python (requirements.txt, pyproject.toml)
- Go (go.mod)
- Rust (Cargo.toml)
"""
import os
import sys
import json
import argparse
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict


# fmt: off
__all__ = ['Dict', 'List', 'Optional', 'Path', 'Set', 'Tuple', 'argparse', 'defaultdict', 'json', 'os', 're', 'sys']  # noqa: E501
# fmt: on
