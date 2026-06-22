# ruff: noqa: E501
#!/usr/bin/env python3
"""
headline_scorer.py — Scores headlines 0-100
Usage:
  python3 headline_scorer.py "Your headline here"
  python3 headline_scorer.py --file headlines.txt
  python3 headline_scorer.py --json
  python3 headline_scorer.py          # demo mode
"""

import argparse
import json
import re
import sys


# ---------------------------------------------------------------------------
# Word lists
# ---------------------------------------------------------------------------

__all__ = ['argparse', 'json', 're', 'sys']
