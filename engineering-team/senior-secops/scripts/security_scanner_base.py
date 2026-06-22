# ruff: noqa: F403, F405, E501
"""
Security Scanner - Scan source code for security vulnerabilities.

Table of Contents:
    SecurityScanner - Main class for security scanning
        __init__         - Initialize with target path and options
        scan()           - Run all security scans
        scan_secrets()   - Detect hardcoded secrets
        scan_sql_injection() - Detect SQL injection patterns
        scan_xss()       - Detect XSS vulnerabilities
        scan_command_injection() - Detect command injection
        scan_path_traversal() - Detect path traversal
        _scan_file()     - Scan individual file for patterns
        _calculate_severity() - Calculate finding severity
    main() - CLI entry point

Usage:
    python security_scanner.py /path/to/project
    python security_scanner.py /path/to/project --severity high
    python security_scanner.py /path/to/project --output report.json --json
"""
import os
import sys
import json
import re
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime


# fmt: off
__all__ = ['Dict', 'List', 'Optional', 'Path', 'Tuple', 'argparse', 'asdict', 'dataclass', 'datetime', 'json', 'os', 're', 'sys']  # noqa: E501
# fmt: on
