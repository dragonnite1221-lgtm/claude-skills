# ruff: noqa: E501
#!/usr/bin/env python3
"""
ai_threat_scanner.py — AI/LLM Security Threat Scanner

Scans for prompt injection patterns, jailbreak attempts, model inversion risk,
data poisoning indicators, and AI agent integrity violations. Maps findings to
MITRE ATLAS techniques.

IMPORTANT: Use --authorized flag only for systems you have authorization to test.

Usage:
    python3 ai_threat_scanner.py --target-type llm --access-level black-box --json
    python3 ai_threat_scanner.py --target-type llm --test-file prompts.json --access-level gray-box --authorized --json
    python3 ai_threat_scanner.py --list-patterns

Exit codes:
    0  Low risk — no critical findings
    1  Medium/High risk findings detected
    2  Critical findings or missing authorization for invasive tests
"""

import argparse
import json
import re
import sys

__all__ = ['argparse', 'json', 're', 'sys']
