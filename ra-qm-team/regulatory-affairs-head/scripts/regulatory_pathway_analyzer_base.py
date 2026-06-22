# ruff: noqa: F403, F405, E501
"""
Regulatory Pathway Analyzer - Determines optimal regulatory pathway for medical devices.

Analyzes device characteristics and recommends the most efficient regulatory pathway
across multiple markets (FDA, EU MDR, UK UKCA, Health Canada, TGA, PMDA).

Supports:
- FDA: 510(k), De Novo, PMA, Breakthrough Device
- EU MDR: Class I, IIa, IIb, III, AIMDD
- UK: UKCA marking
- Health Canada: Class I-IV
- TGA: Class I, IIa, IIb, III
- Japan PMDA: Class I-IV

Usage:
    python regulatory_pathway_analyzer.py --device-class II --predicate yes --market all
    python regulatory_pathway_analyzer.py --interactive
    python regulatory_pathway_analyzer.py --data device_profile.json --output json
"""
import argparse
import json
import sys
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Tuple
from enum import Enum


# fmt: off
__all__ = ['Dict', 'Enum', 'List', 'Optional', 'Tuple', 'argparse', 'asdict', 'dataclass', 'field', 'json', 'sys']  # noqa: E501
# fmt: on
