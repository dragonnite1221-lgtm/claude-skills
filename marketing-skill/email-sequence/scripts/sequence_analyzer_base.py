# ruff: noqa: E501
#!/usr/bin/env python3
"""
sequence_analyzer.py — Email sequence quality analyzer
Usage:
  python3 sequence_analyzer.py --file sequence.json
  python3 sequence_analyzer.py --json
  python3 sequence_analyzer.py          # demo mode

Input JSON format:
  [
    {"subject": "...", "body": "...", "delay_days": 0},
    {"subject": "...", "body": "...", "delay_days": 2},
    ...
  ]
"""

import argparse
import json
import re
import sys


# ---------------------------------------------------------------------------
# Word/pattern lists
# ---------------------------------------------------------------------------

__all__ = ['argparse', 'json', 're', 'sys']
