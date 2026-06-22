# ruff: noqa: E501
#!/usr/bin/env python3
"""
ai_content_detector.py — Detect AI-generated content patterns.

Three detection methods:
  1. Burstiness analysis — human writing has high variance in sentence length;
     AI writing has consistently medium-length sentences
  2. Vocabulary diversity (Type-Token Ratio) — AI reuses words more than humans
  3. Known AI phrases — specific phrases that appear disproportionately in
     AI-generated text

This is a heuristic tool, NOT a proof engine. False positives are expected.
The goal is to flag passages that FEEL AI-generated so a human editor can
inject voice, variance, and specificity.

Usage:
    python ai_content_detector.py article.md
    python ai_content_detector.py article.md --json
    python ai_content_detector.py --demo

Scoring:
    0-20   = likely human (high burstiness, diverse vocab, no AI phrases)
    21-50  = mixed signals (review flagged passages)
    51-100 = likely AI (flat burstiness, repetitive vocab, AI phrase density)
"""
from __future__ import annotations
import argparse
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path

# --- Known AI phrases (commonly overrepresented in LLM output) ---

__all__ = ['Counter', 'Path', 'annotations', 'argparse', 'json', 'math', 're', 'sys']
