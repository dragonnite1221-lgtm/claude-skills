# ruff: noqa: E501
#!/usr/bin/env python3
"""
conversion_audit.py — CRO audit for HTML pages
Usage:
  python3 conversion_audit.py --file page.html
  python3 conversion_audit.py --url https://example.com
  python3 conversion_audit.py --json
  python3 conversion_audit.py          # demo mode
"""

import argparse
import json
import re
import sys
import urllib.request
from html.parser import HTMLParser


# ---------------------------------------------------------------------------
# HTML Parser
# ---------------------------------------------------------------------------

__all__ = ['HTMLParser', 'argparse', 'json', 're', 'sys', 'urllib']
