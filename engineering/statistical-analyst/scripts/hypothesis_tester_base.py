# ruff: noqa: E501
#!/usr/bin/env python3
"""
hypothesis_tester.py — Z-test (proportions), Welch's t-test (means), Chi-square (categorical).

All math uses Python stdlib (math module only). No scipy, numpy, or pandas required.

Usage:
    python3 hypothesis_tester.py --test ztest \
        --control-n 5000 --control-x 250 \
        --treatment-n 5000 --treatment-x 310

    python3 hypothesis_tester.py --test ttest \
        --control-mean 42.3 --control-std 18.1 --control-n 800 \
        --treatment-mean 46.1 --treatment-std 19.4 --treatment-n 820

    python3 hypothesis_tester.py --test chi2 \
        --observed "120,80,50" --expected "100,100,50"
"""

import argparse
import json
import math
import sys


# ---------------------------------------------------------------------------
# Normal / t-distribution approximations (stdlib only)
# ---------------------------------------------------------------------------

__all__ = ['argparse', 'json', 'math', 'sys']
