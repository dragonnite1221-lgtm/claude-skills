# ruff: noqa: E501
#!/usr/bin/env python3
"""
Form Field Analyzer for CRO

Analyzes HTML forms for conversion optimization opportunities.
Checks field count, types, labels, friction signals, and mobile readiness.

Usage:
  python3 form_field_analyzer.py                    # Demo mode
  python3 form_field_analyzer.py form.html          # Analyze HTML file
  python3 form_field_analyzer.py form.html --json   # JSON output
"""

import json
import sys
import os
import re
from html.parser import HTMLParser

__all__ = ['HTMLParser', 'json', 'os', 're', 'sys']
