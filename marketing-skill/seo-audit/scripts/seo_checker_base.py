# ruff: noqa: E501
#!/usr/bin/env python3
"""
seo_checker.py — On-page SEO analyzer
Usage:
  python3 seo_checker.py [--file page.html] [--url https://...] [--json]
  python3 seo_checker.py          # demo mode with embedded sample HTML
"""

import argparse
import json
import math
import re
import sys
import urllib.request
from html.parser import HTMLParser


# ---------------------------------------------------------------------------
# HTML Parser
# ---------------------------------------------------------------------------

__all__ = ['HTMLParser', 'argparse', 'json', 'math', 're', 'sys', 'urllib']
