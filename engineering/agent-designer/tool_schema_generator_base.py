# ruff: noqa: F403, F405, E501
"""
Tool Schema Generator - Generate structured tool schemas for AI agents

Given a description of desired tools (name, purpose, inputs, outputs), generates
structured tool schemas compatible with OpenAI function calling format and 
Anthropic tool use format. Includes: input validation rules, error response 
formats, example calls, rate limit suggestions.

Input: tool descriptions JSON
Output: tool schemas (OpenAI + Anthropic format) + validation rules + example usage
"""
import json
import argparse
import sys
import re
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum


# fmt: off
__all__ = ['Any', 'Dict', 'Enum', 'List', 'Optional', 'Tuple', 'Union', 'argparse', 'asdict', 'dataclass', 'json', 're', 'sys']  # noqa: E501
# fmt: on
