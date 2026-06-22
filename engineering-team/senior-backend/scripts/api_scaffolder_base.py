# ruff: noqa: F403, F405, E501
"""
API Scaffolder

Generates Express.js route handlers, validation middleware, and TypeScript types
from OpenAPI specifications (YAML/JSON).

Usage:
    python api_scaffolder.py openapi.yaml --output src/routes/
    python api_scaffolder.py openapi.json --framework fastify --output src/
    python api_scaffolder.py spec.yaml --types-only --output src/types/
"""
import os
import sys
import json
import argparse
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime


# fmt: off
__all__ = ['Any', 'Dict', 'List', 'Optional', 'Path', 'argparse', 'datetime', 'json', 'os', 're', 'sys']  # noqa: E501
# fmt: on
