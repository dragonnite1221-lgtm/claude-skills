---
title: "Dependency Auditor — Agent Skill for Codex & OpenClaw"
description: "Audit project dependencies for security vulnerabilities (CVE matching with CVSS scores), license compliance/conflicts, and safe upgrade paths across. Agent skill for Claude Code, Codex CLI, Gemini CLI, OpenClaw."
---

# Dependency Auditor

<div class="page-meta" markdown>
<span class="meta-badge">:material-rocket-launch: Engineering - POWERFUL</span>
<span class="meta-badge">:material-identifier: `dependency-auditor`</span>
<span class="meta-badge">:material-github: <a href="https://github.com/alirezarezvani/claude-skills/tree/main/engineering/dependency-auditor/SKILL.md">Source</a></span>
</div>

<div class="install-banner" markdown>
<span class="install-label">Install:</span> <code>claude /plugin install engineering-advanced-skills</code>
</div>


Audits multi-language project dependencies for vulnerabilities, license risk, and
upgrade safety. Three stdlib-only CLI tools generate a shared dependency inventory
(JSON) that flows between them.

## Tools

| Tool | Purpose |
|------|---------|
| `scripts/dep_scanner.py` | Scan a project for known CVEs (with CVSS scores) across npm/pip/go/cargo/etc. |
| `scripts/license_checker.py` | Detect licenses and flag compatibility conflicts against a policy |
| `scripts/upgrade_planner.py` | Turn a dependency inventory into a risk-ranked upgrade plan |

## Audit workflow

Run the gates in order. On a failure, fix the reported issues and re-run that step
before continuing.

```bash
# 1. Vulnerability scan. --fail-on-high exits non-zero on HIGH/CRITICAL CVEs (CI gate).
#    --format json emits the dependency inventory other tools consume.
python scripts/dep_scanner.py /path/to/project --format json --output inventory.json
python scripts/dep_scanner.py /path/to/project --fail-on-high     # CI security gate
python scripts/dep_scanner.py . --quick-scan                       # skip transitive deps

# 2. License compliance. Reuse the inventory from step 1 to avoid re-parsing.
python scripts/license_checker.py /path/to/project --policy strict --warn-conflicts
python scripts/license_checker.py . --inventory inventory.json --format json

# 3. Upgrade plan from the inventory. Risk-rank and bound the rollout window.
python scripts/upgrade_planner.py inventory.json --risk-threshold medium --timeline 60
python scripts/upgrade_planner.py inventory.json --security-only   # security fixes only
```

`--policy` accepts `permissive` or `strict`. `--risk-threshold` accepts
`safe|low|medium|high|critical` (default `high`) and caps which upgrades are
included. Output is `text` (default) or `json`; `--output FILE` writes to disk.

## What each tool reports

**`dep_scanner.py`** — parses manifests and lockfiles for npm, Python, Go, Rust,
Ruby, Maven, PHP, and .NET; matches dependencies against a built-in CVE database
and reports severity, CVSS score, affected/fixed versions, and the dependency path.
Resolves transitive dependencies from lockfiles unless `--quick-scan`.

**`license_checker.py`** — classifies licenses as permissive (MIT, Apache-2.0, BSD,
ISC), strong copyleft (GPL, AGPL), weak copyleft (LGPL, MPL), proprietary, or
unknown, and flags incompatible combinations (e.g. GPL contamination in a permissive
project). See [license_compatibility_matrix.md](https://github.com/alirezarezvani/claude-skills/tree/main/engineering/dependency-auditor/references/license_compatibility_matrix.md).

**`upgrade_planner.py`** — reads the inventory JSON, classifies each update as
patch/minor/major via semver, scores breaking-change risk, orders upgrades by risk
and security priority, and produces a migration checklist within `--timeline` days.

## Inventory format

`dep_scanner.py --format json` produces the inventory consumed by the other tools:
`{ timestamp, project_path, dependencies: [{ name, version, ecosystem, direct,
license, vulnerabilities: [...] }] }`. Sample manifests live in `assets/`
(`sample_package.json`, `sample_requirements.txt`, `sample_go.mod`); reference
outputs are in `expected_outputs/`.

## References

- [vulnerability_assessment_guide.md](https://github.com/alirezarezvani/claude-skills/tree/main/engineering/dependency-auditor/references/vulnerability_assessment_guide.md) — CVE/CVSS scoring, triage, false-positive handling
- [license_compatibility_matrix.md](https://github.com/alirezarezvani/claude-skills/tree/main/engineering/dependency-auditor/references/license_compatibility_matrix.md) — license classes and conflict rules
- [dependency_management_best_practices.md](https://github.com/alirezarezvani/claude-skills/tree/main/engineering/dependency-auditor/references/dependency_management_best_practices.md) — scan cadence, upgrade hygiene, supply-chain risk
