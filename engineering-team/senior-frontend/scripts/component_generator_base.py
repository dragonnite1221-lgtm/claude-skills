# ruff: noqa: E501
#!/usr/bin/env python3
"""
React Component Generator

Generates React/Next.js component files with TypeScript, Tailwind CSS,
and optional test files following best practices.

Usage:
    python component_generator.py Button --dir src/components/ui
    python component_generator.py ProductCard --type client --with-test
    python component_generator.py UserProfile --type server --with-story
"""

import argparse
import os
import sys
from pathlib import Path
from datetime import datetime


# Component templates

__all__ = ['Path', 'argparse', 'datetime', 'os', 'sys']
