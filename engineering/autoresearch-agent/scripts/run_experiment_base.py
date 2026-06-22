# ruff: noqa: E501
#!/usr/bin/env python3
"""
autoresearch-agent: Experiment Runner

Executes a single experiment iteration. The AI agent is the loop —
it calls this script repeatedly. The script handles evaluation,
metric parsing, keep/discard decisions, and git rollback on failure.

Usage:
    python scripts/run_experiment.py --experiment engineering/api-speed --single
    python scripts/run_experiment.py --experiment engineering/api-speed --dry-run
    python scripts/run_experiment.py --experiment engineering/api-speed --single --description "added caching"
"""

import argparse
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

__all__ = ['Path', 'argparse', 'datetime', 'subprocess', 'sys', 'time']
