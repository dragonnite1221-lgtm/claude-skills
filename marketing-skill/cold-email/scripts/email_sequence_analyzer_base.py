# ruff: noqa: E501
#!/usr/bin/env python3
"""
email_sequence_analyzer.py — Analyzes a cold email sequence for quality signals.

Evaluates each email on:
  - Word count (shorter is usually better for cold email)
  - Reading level estimate (Flesch-Kincaid approximation via avg sentence/word length)
  - Personalization density (signals of specific, targeted writing)
  - CTA clarity (is there a clear ask?)
  - Spam trigger words (words that hurt deliverability)
  - Subject line analysis (length, warning patterns)
  - Overall score: 0-100

Usage:
    python3 email_sequence_analyzer.py [sequence.json]
    cat sequence.json | python3 email_sequence_analyzer.py

If no file provided, runs on embedded sample sequence.

Input format (JSON):
    [
      {
        "email": 1,
        "subject": "...",
        "body": "..."
      },
      ...
    ]

Stdlib only — no external dependencies.
"""

import json
import re
import sys
import math
import select
from typing import List, Dict, Any


# ─── Spam trigger words ───────────────────────────────────────────────────────

__all__ = ['Any', 'Dict', 'List', 'json', 'math', 're', 'select', 'sys']
