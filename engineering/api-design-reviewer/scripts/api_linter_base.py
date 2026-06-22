# ruff: noqa: F403, F405, E501
"""
API Linter - Analyzes OpenAPI/Swagger specifications for REST conventions and best practices.

This script validates API designs against established conventions including:
- Resource naming conventions (kebab-case resources, camelCase fields)
- HTTP method usage patterns
- URL structure consistency
- Error response format standards
- Documentation completeness
- Pagination patterns
- Versioning compliance

Supports both OpenAPI JSON specifications and raw endpoint definition JSON.
"""
import argparse
import json
import re
import sys
from typing import Any, Dict, List, Tuple, Optional, Set
from urllib.parse import urlparse
from dataclasses import dataclass, field


# fmt: off
__all__ = ['Any', 'Dict', 'List', 'Optional', 'Set', 'Tuple', 'argparse', 'dataclass', 'field', 'json', 're', 'sys', 'urlparse']  # noqa: E501
# fmt: on
