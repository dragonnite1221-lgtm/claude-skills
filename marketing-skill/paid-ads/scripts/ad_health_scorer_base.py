# ruff: noqa: E501
#!/usr/bin/env python3
"""
ad_health_scorer.py — Weighted 0-100 ad account health score with multi-platform support.

Scores ad accounts across platform-specific categories with severity multipliers
and budget-weighted cross-platform aggregation.

Severity multipliers:
  critical = 5x weight (blocks revenue or burns budget)
  high     = 3x weight (significant impact)
  medium   = 1.5x weight (optimization opportunity)
  low      = 0.5x weight (backlog polish)

Platform category weights:
  Google:   Conversion Tracking 25%, Wasted Spend 20%, Structure 15%, Keywords 15%, Ads 15%, Settings 10%
  Meta:     Pixel/CAPI 30%, Creative 30%, Structure 20%, Audience 20%
  LinkedIn: Technical 25%, Targeting 25%, Creative 25%, Budget 25%
  TikTok:   Pixel 25%, Creative 30%, Targeting 25%, Budget 20%

Cross-platform aggregation:
  Aggregate Score = Σ(Platform_Score × Platform_Budget_Share)

Grade bands (calibrated wider — ad accounts naturally score lower):
  A = 90-100, B = 75-89, C = 60-74, D = 40-59, F = <40

Usage:
    python ad_health_scorer.py --checks checks.json
    python ad_health_scorer.py --checks checks.json --platform google --budget 5000
    python ad_health_scorer.py --multi platforms.json   # multi-platform aggregation
    python ad_health_scorer.py --demo
    python ad_health_scorer.py --demo --json
"""
from __future__ import annotations
import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

__all__ = ['Path', 'annotations', 'argparse', 'defaultdict', 'json', 'sys']
