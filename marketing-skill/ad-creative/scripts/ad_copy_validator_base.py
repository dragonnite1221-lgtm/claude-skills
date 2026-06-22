# ruff: noqa: E501
#!/usr/bin/env python3
"""
ad_copy_validator.py — Validates ad copy against platform specs.

Checks: character counts, rejection triggers (ALL CAPS, excessive punctuation,
trademarked terms), and scores each ad 0-100.

Usage:
    python3 ad_copy_validator.py                  # runs embedded sample
    python3 ad_copy_validator.py ads.json         # validates a JSON file
    echo '{"platform":"google_rsa","headlines":["My headline"]}' | python3 ad_copy_validator.py

JSON input format:
    {
      "platform": "google_rsa" | "meta_feed" | "linkedin" | "twitter" | "tiktok",
      "headlines": ["...", ...],
      "descriptions": ["...", ...],   # for google
      "primary_text": "...",          # for meta, linkedin, twitter, tiktok
      "headline": "...",              # for meta headline field
      "intro_text": "..."             # for linkedin
    }
"""

import json
import re
import sys
from collections import defaultdict

# ---------------------------------------------------------------------------
# Platform specifications
# ---------------------------------------------------------------------------

__all__ = ['defaultdict', 'json', 're', 'sys']
