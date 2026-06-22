# ruff: noqa: E501
#!/usr/bin/env python3
"""
Expansion Opportunity Scorer

Analyses customer product adoption depth, maps whitespace for unused
features/products, estimates revenue opportunities, and prioritises
expansion plays by effort vs impact.

Usage:
    python expansion_opportunity_scorer.py customer_data.json
    python expansion_opportunity_scorer.py customer_data.json --format json
"""

import argparse
import json
import sys
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Tier pricing multipliers (relative to current plan price)

__all__ = ['Any', 'Dict', 'List', 'Optional', 'Tuple', 'argparse', 'json', 'sys']
