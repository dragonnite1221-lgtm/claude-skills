# ruff: noqa: E501
#!/usr/bin/env python3
"""
engagement_planner.py — Red Team Engagement Planner

Builds a structured red team engagement plan from target scope, MITRE ATT&CK
technique selection, access level, and crown jewel assets. Scores techniques
by detection risk and effort, assembles kill-chain phases, identifies choke
points, and generates OPSEC risk items.

IMPORTANT: Authorization is required. Use --authorized flag only after obtaining
signed Rules of Engagement (RoE) and written executive authorization.

Usage:
    python3 engagement_planner.py --techniques T1059,T1078,T1003 --access-level external --authorized --json
    python3 engagement_planner.py --techniques T1059,T1078 --crown-jewels "DB,AD" --access-level credentialed --authorized --json
    python3 engagement_planner.py --list-techniques

Exit codes:
    0  Engagement plan generated successfully
    1  Missing authorization or invalid input
    2  Scope violation or technique outside access-level constraints
"""

import argparse
import json
import sys

__all__ = ['argparse', 'json', 'sys']
