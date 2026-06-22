# ruff: noqa: E501
#!/usr/bin/env python3
"""
Architecture Diagram Generator

Generates architecture diagrams from project structure in multiple formats:
- Mermaid (default)
- PlantUML
- ASCII

Supports diagram types:
- component: Shows modules and their relationships
- layer: Shows architectural layers
- deployment: Shows deployment topology
"""

import os
import sys
import json
import argparse
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict

__all__ = ['Dict', 'List', 'Optional', 'Path', 'Set', 'Tuple', 'argparse', 'defaultdict', 'json', 'os', 're', 'sys']
