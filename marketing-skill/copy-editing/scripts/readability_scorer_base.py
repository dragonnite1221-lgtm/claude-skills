# ruff: noqa: E501
#!/usr/bin/env python3
"""
readability_scorer.py — Readability metrics for marketing copy
Usage:
  python3 readability_scorer.py --file copy.txt
  echo "Your text here" | python3 readability_scorer.py
  python3 readability_scorer.py          # demo mode
  python3 readability_scorer.py --json
"""

import argparse
import json
import math
import re
import sys


# ---------------------------------------------------------------------------
# Word lists
# ---------------------------------------------------------------------------

__all__ = ['argparse', 'json', 'math', 're', 'sys']
