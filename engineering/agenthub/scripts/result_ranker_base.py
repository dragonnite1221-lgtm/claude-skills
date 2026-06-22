# ruff: noqa: E501
#!/usr/bin/env python3
"""Rank AgentHub agent results by metric or diff quality.

Runs an evaluation command in each agent's worktree, parses a metric,
and produces a ranked table.

Usage:
    python result_ranker.py --session 20260317-143022 \\
        --eval-cmd "pytest bench.py --json" --metric p50_ms --direction lower

    python result_ranker.py --session 20260317-143022 --diff-summary

    python result_ranker.py --demo
"""

import argparse
import json
import os
import re
import subprocess
import sys

__all__ = ['argparse', 'json', 'os', 're', 'subprocess', 'sys']
