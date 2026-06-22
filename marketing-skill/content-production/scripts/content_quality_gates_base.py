# ruff: noqa: E501
#!/usr/bin/env python3
"""
content_quality_gates.py — Non-negotiable quality checks before publishing.

Hard stops that BLOCK publication. These aren't suggestions — they're rules.
Inspired by the quality gate pattern used in high-traction content tools.

Gates (all must pass):
  1. Heading hierarchy: H1 → H2 → H3 only (no skips, no H4+ without H3)
  2. No paragraphs > 150 words (wall of text)
  3. All images/figures have alt text references
  4. Source citations: any statistic must have a [source] marker
  5. Title length: 50-60 characters
  6. Meta description: 150-160 characters (if present)
  7. No self-promotional mentions beyond 1
  8. dateModified or "Updated" marker present for evergreen content

Usage:
    python content_quality_gates.py article.md
    python content_quality_gates.py article.md --json
    python content_quality_gates.py --demo

Score bands (from the gate results):
    All pass         → PUBLISH (ready to ship)
    1-2 warnings     → TARGET (fix specific items)
    Any gate failure  → BLOCK (fix before publishing)
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path

__all__ = ['Path', 'annotations', 'argparse', 'json', 're', 'sys']
