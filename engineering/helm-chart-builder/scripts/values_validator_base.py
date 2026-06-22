# ruff: noqa: E501
#!/usr/bin/env python3
"""
helm-chart-builder: Values Validator

Validate values.yaml files against Helm best practices — documentation coverage,
type consistency, naming conventions, default quality, and security.

Usage:
    python scripts/values_validator.py values.yaml
    python scripts/values_validator.py values.yaml --output json
    python scripts/values_validator.py values.yaml --strict
"""

import argparse
import json
import re
import sys
from pathlib import Path


# --- Demo values.yaml ---

__all__ = ['Path', 'argparse', 'json', 're', 'sys']
