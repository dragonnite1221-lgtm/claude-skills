# ruff: noqa: E501
#!/usr/bin/env python3
"""
comparison_matrix_builder.py — Competitive Feature Comparison Matrix Builder
100% stdlib, no pip installs required.

Usage:
    python3 comparison_matrix_builder.py                        # demo mode
    python3 comparison_matrix_builder.py --input matrix.json
    python3 comparison_matrix_builder.py --input matrix.json --json
    python3 comparison_matrix_builder.py --input matrix.json --markdown > comparison.md

matrix.json format:
    {
      "your_product": "YourProduct",
      "features": [
        {
          "name": "SSO / SAML",
          "category": "Security",
          "your_status": "full",           # full | partial | no | planned
          "competitors": {
            "CompetitorA": "no",
            "CompetitorB": "partial",
            "CompetitorC": "full"
          },
          "notes": "Enterprise tier only"  # optional
        }
      ]
    }
"""

import argparse
import json
import sys
from collections import defaultdict


# ---------------------------------------------------------------------------
# Status helpers
# ---------------------------------------------------------------------------

__all__ = ['argparse', 'defaultdict', 'json', 'sys']
