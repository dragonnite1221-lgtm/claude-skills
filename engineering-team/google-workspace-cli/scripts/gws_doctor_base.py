# ruff: noqa: E501
#!/usr/bin/env python3
"""
Google Workspace CLI Doctor — Pre-flight diagnostics for gws CLI.

Checks installation, version, authentication status, and service
connectivity. Runs in demo mode with embedded sample data when gws
is not installed.

Usage:
    python3 gws_doctor.py
    python3 gws_doctor.py --json
    python3 gws_doctor.py --services gmail,drive,calendar
"""

import argparse
import json
import shutil
import subprocess
import sys
from dataclasses import dataclass, field, asdict
from typing import List, Optional

__all__ = ['List', 'Optional', 'argparse', 'asdict', 'dataclass', 'field', 'json', 'shutil', 'subprocess', 'sys']
