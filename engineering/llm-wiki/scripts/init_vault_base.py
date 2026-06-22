# ruff: noqa: E501
#!/usr/bin/env python3
"""
init_vault.py — Bootstrap an LLM Wiki vault.

Creates the three-layer structure (raw/, wiki/, schema files) and seeds it with
starter templates for CLAUDE.md, AGENTS.md, index.md, log.md, and page templates.

Usage:
    python init_vault.py --path ~/vaults/research --topic "LLM interpretability"
    python init_vault.py --path ./my-wiki --topic "Book: The Power Broker" --tool codex

The --tool flag controls which schema file(s) to install:
    claude-code  → CLAUDE.md (default)
    codex        → AGENTS.md
    cursor       → AGENTS.md + .cursorrules
    antigravity  → AGENTS.md
    all          → CLAUDE.md + AGENTS.md + .cursorrules (recommended for multi-tool)
"""
from __future__ import annotations
import argparse
import datetime as dt
import json
import sys
from pathlib import Path

__all__ = ['Path', 'annotations', 'argparse', 'dt', 'json', 'sys']
