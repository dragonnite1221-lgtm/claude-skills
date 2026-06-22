# ruff: noqa: E501
#!/usr/bin/env python3
"""WCAG 2.2 Accessibility Scanner for Frontend Codebases.

Scans HTML, JSX, TSX, Vue, Svelte, and CSS files for accessibility
violations across 10 categories: images, forms, headings, landmarks,
keyboard, ARIA, color/contrast, links, tables, and media.

Usage:
    python a11y_scanner.py /path/to/project
    python a11y_scanner.py /path/to/project --json
    python a11y_scanner.py /path/to/project --severity critical,serious
    python a11y_scanner.py /path/to/project --format json
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, asdict
from typing import List, Optional

__all__ = ['List', 'Optional', 'argparse', 'asdict', 'dataclass', 'json', 'os', 're', 'sys']
