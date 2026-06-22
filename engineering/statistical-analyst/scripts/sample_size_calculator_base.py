# ruff: noqa: E501
#!/usr/bin/env python3
from __future__ import annotations
"""
sample_size_calculator.py — Required sample size per variant for A/B experiments.

Supports proportion tests (conversion rates) and mean tests (continuous metrics).
All math uses Python stdlib only.

Usage:
    python3 sample_size_calculator.py --test proportion \
        --baseline 0.05 --mde 0.20 --alpha 0.05 --power 0.80

    python3 sample_size_calculator.py --test mean \
        --baseline-mean 42.3 --baseline-std 18.1 --mde 0.10 \
        --alpha 0.05 --power 0.80

    python3 sample_size_calculator.py --test proportion \
        --baseline 0.05 --mde 0.20 --table

    python3 sample_size_calculator.py --test proportion \
        --baseline 0.05 --mde 0.20 --format json
"""

import argparse
import json
import math
import sys

__all__ = ['annotations', 'argparse', 'json', 'math', 'sys']
