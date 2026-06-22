# ruff: noqa: E501
#!/usr/bin/env python3
"""
Decision Matrix Scorer — Executive Mentor Tool

Weighted multi-criteria decision analysis with sensitivity testing.
Answers: Which option wins? How fragile is that result? Where are the close calls?

Usage:
    python decision_matrix_scorer.py                    # Run with sample data
    python decision_matrix_scorer.py --interactive      # Interactive mode
    python decision_matrix_scorer.py --file data.json   # Load from JSON file

JSON format:
    {
        "decision": "Description of the decision",
        "criteria": [
            {"name": "Criterion Name", "weight": 0.3, "description": "Optional"},
            ...
        ],
        "options": [
            {
                "name": "Option Name",
                "description": "Optional description",
                "scores": {"Criterion Name": 8, "Another": 6, ...}
            },
            ...
        ]
    }

Scores: 1–10 scale. Weights: must sum to 1.0 (or will be normalized).
"""

import json
import sys
import argparse
from typing import List, Dict, Tuple

# ─────────────────────────────────────────────────────
# Core data structures
# ─────────────────────────────────────────────────────

__all__ = ['Dict', 'List', 'Tuple', 'argparse', 'json', 'sys']
