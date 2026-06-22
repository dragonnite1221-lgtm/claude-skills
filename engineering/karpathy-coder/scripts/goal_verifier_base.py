# ruff: noqa: E501
#!/usr/bin/env python3
"""
goal_verifier.py — Check if a plan has verifiable success criteria.

Karpathy Principle #4 (Goal-Driven Execution): "Define success criteria.
Loop until verified. Don't tell it what to do — give it success criteria
and watch it go."

Reads a markdown plan and scores:
  - Does each step have a verification check?
  - Are success criteria concrete (test, assertion, measurement)?
  - Are there vague criteria ("make it work", "looks good")?
  - Is there a final verification step?

Usage:
    python goal_verifier.py plan.md
    python goal_verifier.py plan.md --json

Scoring:
    Each plan step gets 0-3 points:
      3 = concrete verification (test assertion, metric, command)
      2 = reasonable verification (manual check, visual)
      1 = vague verification ("should work", "looks right")
      0 = no verification mentioned
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path

__all__ = ['Path', 'annotations', 'argparse', 'json', 're', 'sys']
