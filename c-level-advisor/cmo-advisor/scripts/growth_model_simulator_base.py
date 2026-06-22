# ruff: noqa: E501
#!/usr/bin/env python3
"""
Growth Model Simulator
----------------------
Projects MRR growth across different growth models (PLG, sales-led, community-led,
hybrid) and shows the impact of channel mix changes on growth trajectory.

Usage:
    python growth_model_simulator.py

Inputs (edit INPUTS section):
    - Starting MRR and churn rate
    - Current channel mix (% of new MRR from each source)
    - Conversion rates per model
    - Growth rate assumptions per channel

Outputs:
    - 12-month MRR projection by growth model
    - Channel mix impact analysis (what happens if you shift mix)
    - Break-even months for each model
    - Side-by-side comparison table
"""

from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

__all__ = ['Dict', 'List', 'Optional', 'Tuple', 'annotations', 'dataclass', 'field', 'math']
