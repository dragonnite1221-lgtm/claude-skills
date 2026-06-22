# ruff: noqa: E501
#!/usr/bin/env python3
"""Analyze any codebase (frontend, backend, or fullstack) and extract routes, APIs, models, and structure.

Supports: React, Vue, Angular, Svelte, Next.js, Nuxt, NestJS, Express, Django, FastAPI, Flask.
Stdlib only — no third-party dependencies. Outputs JSON for downstream PRD generation.

Usage:
    python3 codebase_analyzer.py /path/to/project
    python3 codebase_analyzer.py /path/to/project --output prd-analysis.json
    python3 codebase_analyzer.py /path/to/project --format markdown
"""

import argparse
import json
import os
import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

__all__ = ['Any', 'Dict', 'List', 'Optional', 'Path', 'Set', 'Tuple', 'argparse', 'defaultdict', 'json', 'os', 're']
