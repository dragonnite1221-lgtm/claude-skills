# ruff: noqa: E501
#!/usr/bin/env python3
"""
docker-development: Docker Compose Validator

Validate docker-compose.yml files for best practices, missing healthchecks,
network configuration, port conflicts, and security issues.

Usage:
    python scripts/compose_validator.py docker-compose.yml
    python scripts/compose_validator.py docker-compose.yml --output json
    python scripts/compose_validator.py docker-compose.yml --strict
"""

import argparse
import json
import re
import sys
from pathlib import Path


# --- Demo Compose File ---

__all__ = ['Path', 'argparse', 'json', 're', 'sys']
