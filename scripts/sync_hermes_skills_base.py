# ruff: noqa: E501
#!/usr/bin/env python3
"""
sync-hermes-skills.py — Install claude-code-skills into Hermes Agent.

Hermes Agent (https://github.com/NousResearch/hermes-agent) discovers skills
from ~/.hermes/skills/. This script creates symlinks from our repo's skill
directories into Hermes's skill directory, preserving the category structure.

Both tools use the agentskills.io standard (SKILL.md with YAML frontmatter),
so no format conversion is needed — just symlink the directories.

Usage:
    python scripts/sync-hermes-skills.py                   # full sync
    python scripts/sync-hermes-skills.py --verbose          # show each skill
    python scripts/sync-hermes-skills.py --domain engineering  # one domain
    python scripts/sync-hermes-skills.py --dry-run          # preview only
    python scripts/sync-hermes-skills.py --copy             # copy instead of symlink

Hermes skill directory: ~/.hermes/skills/
Our skills land under:  ~/.hermes/skills/claude-skills/<domain>/<skill-name>/
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

__all__ = ['Path', 'annotations', 'argparse', 'json', 'os', 'shutil', 'sys']
