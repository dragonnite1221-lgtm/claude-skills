# ruff: noqa: E501
#!/usr/bin/env python3
"""
autoresearch-agent: Setup Experiment

Initialize a new experiment with domain, target, evaluator, and git branch.
Creates the .autoresearch/{domain}/{name}/ directory structure.

Usage:
    python scripts/setup_experiment.py --domain engineering --name api-speed \
        --target src/api/search.py --eval "pytest bench.py" \
        --metric p50_ms --direction lower

    python scripts/setup_experiment.py --domain marketing --name medium-ctr \
        --target content/titles.md --eval "python evaluate.py" \
        --metric ctr_score --direction higher --evaluator llm_judge_content

    python scripts/setup_experiment.py --list          # List all experiments
    python scripts/setup_experiment.py --list-evaluators  # List available evaluators
"""

import argparse
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

__all__ = ['Path', 'argparse', 'datetime', 'shutil', 'subprocess', 'sys']
