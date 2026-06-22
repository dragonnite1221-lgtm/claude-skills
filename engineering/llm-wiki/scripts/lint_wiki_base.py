# ruff: noqa: E501
#!/usr/bin/env python3
"""
lint_wiki.py — Health-check an LLM Wiki vault.

Surfaces structural problems the LLM-as-wiki-maintainer should fix:

  - orphans:        pages with zero inbound [[wikilinks]]
  - broken_links:   [[wikilinks]] pointing to non-existent pages
  - stale:          pages whose `updated:` frontmatter is older than --stale-days
  - missing_fm:     pages without a title/category/summary in frontmatter
  - duplicate_titles: two or more pages sharing the same title
  - log_gaps:       no log entry in the last --log-gap-days

Usage:
    python lint_wiki.py --vault ~/vaults/research
    python lint_wiki.py --vault . --stale-days 60 --json
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
