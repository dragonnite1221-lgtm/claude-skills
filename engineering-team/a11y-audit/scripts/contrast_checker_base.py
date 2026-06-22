# ruff: noqa: E501
#!/usr/bin/env python3
"""WCAG 2.2 Color Contrast Checker.

Checks foreground/background color pairs against WCAG 2.2 contrast ratio
thresholds for normal text, large text, and UI components. Supports hex,
rgb(), and named CSS colors.

Usage:
    python contrast_checker.py "#ffffff" "#000000"
    python contrast_checker.py --suggest "#336699"
    python contrast_checker.py --batch styles.css
    python contrast_checker.py --demo
"""

import argparse
import json
import re
import sys

# ---------------------------------------------------------------------------
# Named CSS colors (25 common ones)
# ---------------------------------------------------------------------------

__all__ = ['argparse', 'json', 're', 'sys']
