# ruff: noqa: E501
#!/usr/bin/env python3
"""
Fundraising Model
==================
Cap table management, dilution modeling, and multi-round scenario planning.
Know exactly what you're giving up before you walk into any negotiation.

Covers:
  - Cap table state at each round
  - Dilution per shareholder per round
  - Option pool shuffle impact
  - Multi-round projections (Seed → A → B → C)
  - Return scenarios at different exit valuations

Usage:
    python fundraising_model.py
    python fundraising_model.py --exit 150  # model at $150M exit
    python fundraising_model.py --csv

Stdlib only. No dependencies.
"""

import argparse
import csv
import io
import sys
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

__all__ = ['Optional', 'argparse', 'csv', 'dataclass', 'field', 'io', 'sys']
