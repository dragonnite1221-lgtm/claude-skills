# ruff: noqa: F403, F405, E501
"""
Coverage analysis module.

Parse and analyze test coverage reports in multiple formats (LCOV, JSON, XML).
Identify gaps, calculate metrics, and provide actionable recommendations.
"""
from typing import Dict, List, Any, Optional, Tuple
import json
import xml.etree.ElementTree as ET


# fmt: off
__all__ = ['Any', 'Dict', 'ET', 'List', 'Optional', 'Tuple', 'json']  # noqa: E501
# fmt: on
