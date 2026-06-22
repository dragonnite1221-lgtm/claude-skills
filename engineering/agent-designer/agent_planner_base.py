# ruff: noqa: F403, F405, E501
"""
Agent Planner - Multi-Agent System Architecture Designer

Given a system description (goal, tasks, constraints, team size), designs a multi-agent
architecture: defines agent roles, responsibilities, capabilities needed, communication
topology, tool requirements. Generates architecture diagram (Mermaid).

Input: system requirements JSON
Output: agent architecture + role definitions + Mermaid diagram + implementation roadmap
"""
import json
import argparse
import sys
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum


# fmt: off
__all__ = ['Any', 'Dict', 'Enum', 'List', 'Optional', 'Tuple', 'argparse', 'asdict', 'dataclass', 'json', 'sys']  # noqa: E501
# fmt: on
