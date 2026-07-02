#!/usr/bin/env bash
#
# Single source of truth for the blocking quality checks.
#
# CI (.github/workflows/ci-quality-gate.yml) runs THIS script, and so should
# you locally before pushing:  bash scripts/check.sh
#
# Keeping one script means a local green run and a CI green run check exactly
# the same things (FLEET_QUALITY_INVARIANTS.md, Invariant 2: local == CI).
set -euo pipefail

cd "$(dirname "$0")/.."

echo "==> [1/4] Python syntax (compileall)"
python3 -m compileall -q \
  marketing-skill product-team c-level-advisor \
  engineering-team ra-qm-team engineering \
  business-growth finance project-management scripts

echo "==> [2/4] Skill frontmatter + Gemini mirror gate"
python3 scripts/validate-skill-frontmatter.py

echo "==> [3/4] Inventory drift gate (docs == repo state)"
python3 scripts/count-repository-items.py --check

echo "==> [4/4] Test suite"
python3 -m pytest tests/ --tb=short -q

echo "All quality gates passed."
