# ruff: noqa: E501
#!/usr/bin/env python3
"""
docker-development: Dockerfile Analyzer

Static analysis of Dockerfiles for optimization opportunities, anti-patterns,
and security issues. Reports layer count, base image analysis, and actionable
recommendations.

Usage:
    python scripts/dockerfile_analyzer.py Dockerfile
    python scripts/dockerfile_analyzer.py Dockerfile --output json
    python scripts/dockerfile_analyzer.py Dockerfile --security
"""

import argparse
import json
import re
import sys
from pathlib import Path


# --- Analysis Rules ---

__all__ = ['Path', 'argparse', 'json', 're', 'sys']
