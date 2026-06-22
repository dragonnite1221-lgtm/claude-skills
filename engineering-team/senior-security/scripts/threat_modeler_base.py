# ruff: noqa: E501
#!/usr/bin/env python3
"""
Threat Modeler

Performs STRIDE threat analysis on system components.
Generates threat model documentation with risk scores.

Usage:
    python threat_modeler.py --component "User Authentication"
    python threat_modeler.py --component "API Gateway" --assets "user_data,sessions"
    python threat_modeler.py --interactive
    python threat_modeler.py --list-threats
"""

import argparse
import json
import sys
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum

__all__ = ['Dict', 'Enum', 'List', 'Optional', 'argparse', 'asdict', 'dataclass', 'json', 'sys']
