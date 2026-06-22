# ruff: noqa: E501
#!/usr/bin/env python3
"""
terraform-patterns: Terraform Security Scanner

Scan .tf files for common security issues including hardcoded secrets,
overly permissive IAM policies, open security groups, missing encryption,
and sensitive variable misuse.

Usage:
    python scripts/tf_security_scanner.py ./terraform
    python scripts/tf_security_scanner.py ./terraform --output json
    python scripts/tf_security_scanner.py ./terraform --strict
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path


# --- Demo Terraform File ---

__all__ = ['Path', 'argparse', 'json', 'os', 're', 'sys']
