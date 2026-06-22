# ruff: noqa: E501
#!/usr/bin/env python3
"""
Marketing Budget Modeler
------------------------
Allocates marketing budget across channels based on CAC efficiency and
target MQL volume. Models conservative / moderate / aggressive scenarios.

Usage:
    python marketing_budget_modeler.py

Inputs (edit INPUTS section below or extend with argparse):
    - Annual revenue target (new ARR)
    - Average selling price (ASP)
    - Conversion rates by funnel stage
    - Historical CAC per channel
    - Channel capacity constraints (max MQLs the channel can realistically produce)

Outputs:
    - Required MQL volume by channel
    - Budget allocation per channel per scenario
    - LTV:CAC and payback period per channel
    - Summary table across scenarios
"""

from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import Dict, List, Tuple


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

__all__ = ['Dict', 'List', 'Tuple', 'annotations', 'dataclass', 'field', 'math']
