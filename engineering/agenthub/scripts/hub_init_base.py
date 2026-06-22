# ruff: noqa: E501
#!/usr/bin/env python3
"""Initialize an AgentHub collaboration session.

Creates the .agenthub/ directory structure, generates a session ID,
and writes config.yaml and state.json for the session.

Usage:
    python hub_init.py --task "Optimize API response time" --agents 3 \\
        --eval "pytest bench.py --json" --metric p50_ms --direction lower

    python hub_init.py --task "Refactor auth module" --agents 2

    python hub_init.py --demo
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone

__all__ = ['argparse', 'datetime', 'json', 'os', 'sys', 'timezone']
