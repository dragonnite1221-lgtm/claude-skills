# ruff: noqa: E501
#!/usr/bin/env python3
"""
Google Workspace CLI Auth Setup Guide — Guided authentication configuration.

Prints step-by-step instructions for OAuth and service account setup,
generates .env templates, lists required scopes, and validates auth.

Usage:
    python3 auth_setup_guide.py --guide oauth
    python3 auth_setup_guide.py --guide service-account
    python3 auth_setup_guide.py --scopes gmail,drive,calendar
    python3 auth_setup_guide.py --generate-env
    python3 auth_setup_guide.py --validate [--json]
    python3 auth_setup_guide.py --check [--json]
"""

import argparse
import json
import shutil
import subprocess
import sys
from dataclasses import dataclass, field, asdict
from typing import List, Dict

__all__ = ['Dict', 'List', 'argparse', 'asdict', 'dataclass', 'field', 'json', 'shutil', 'subprocess', 'sys']
