# ruff: noqa: F403, F405, E501
"""
Project Architect

Analyzes project structure and detects:
- Architectural patterns (MVC, layered, hexagonal, microservices)
- Code organization issues (god classes, mixed concerns)
- Layer violations
- Missing architectural components

Provides architecture assessment and improvement recommendations.
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
