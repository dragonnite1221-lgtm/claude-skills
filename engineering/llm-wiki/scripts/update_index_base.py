# ruff: noqa: E501
#!/usr/bin/env python3
"""
update_index.py — Regenerate wiki/index.md from the frontmatter of every wiki page.

The index is content-oriented: a catalog organized by category (entities, concepts,
sources, comparisons, synthesis), with one-line summaries read from each page's
YAML frontmatter.

Frontmatter convention (per page):
    ---
    title: Monosemanticity
    category: concept            # entity | concept | source | comparison | synthesis
    summary: Single-feature interpretability hypothesis from Anthropic's sparse autoencoder work
    tags: [interpretability, sparse-autoencoders]
    sources: 2                   # optional — count of sources referencing this page
    updated: 2026-04-10
    ---

Usage:
    python update_index.py --vault ~/vaults/research
    python update_index.py --vault . --dry-run
"""
from __future__ import annotations
import argparse
import datetime as dt
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

__all__ = ['Path', 'annotations', 'argparse', 'defaultdict', 'dt', 'json', 're', 'sys']
