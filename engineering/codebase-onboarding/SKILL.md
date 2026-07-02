---
name: "codebase-onboarding"
description: "Scan an unfamiliar repository and draft onboarding documentation for new engineers, tech leads, or contractors. codebase_analyzer.py walks the repo to detect languages by extension, key config files (package.json, requirements.txt, Dockerfile, go.mod, etc.), the largest files, and the directory tree, emitting text or --json facts. Reference templates turn those facts into a README/onboarding packet with setup, architecture, key files, common tasks, and debugging sections, tailored by audience. Use when the user wants to onboard onto a new codebase, write or refresh onboarding/handoff docs, or asks 'document this repo for new hires', 'what does this project use', or 'generate an onboarding guide'."
---

# Codebase Onboarding

Analyze a repository and generate onboarding documentation for engineers, tech leads,
and contractors. `codebase_analyzer.py` gathers the facts; the reference templates turn
them into audience-aware docs.

## Tool

| Tool | Purpose |
|------|---------|
| `scripts/codebase_analyzer.py` | Walk a repo and report languages, key config files, largest files, and directory structure |

## Workflow

Run the analyzer, then draft docs from the template. If the analyzer reports "None found
from default checklist" for config files or misses a language, the repo likely uses an
unrecognized manifest — note it manually before writing setup steps.

```bash
# 1. Gather facts (human-readable). --max-depth controls structure depth (default 2).
python3 scripts/codebase_analyzer.py /path/to/repo
python3 scripts/codebase_analyzer.py /path/to/repo --max-depth 3

# 2. Machine-readable facts for templating / CI.
python3 scripts/codebase_analyzer.py /path/to/repo --json
```

`--json` emits `{ root, file_count, languages, key_config_files, top_extensions,
largest_files, structure }`. The analyzer detects languages by extension (Python, JS/TS,
Go, Rust, Java, etc.) and checks for known manifests (package.json, requirements.txt,
pyproject.toml, go.mod, Cargo.toml, Dockerfile, and more).

## Drafting the docs

1. Run the analyzer and capture the signals above.
2. Fill the onboarding template — see [onboarding-template.md](references/onboarding-template.md)
   (full README structure: Quick Start, Architecture, Key Files, Common Developer Tasks,
   Debugging Guide, Contribution Guidelines, audience notes).
3. **Validate setup commands on a clean checkout before publishing** — docs that don't
   reproduce are worse than none.
4. Tailor depth by audience:
   - **Junior:** setup + guardrails
   - **Senior:** architecture + operational concerns
   - **Contractor:** scoped ownership + integration boundaries
5. Export to Notion or Confluence using [output-format-templates.md](references/output-format-templates.md).

## Common pitfalls

- Publishing setup steps that were never run on a clean environment.
- Mixing architecture deep-dives into contractor-scoped docs.
- Omitting troubleshooting/verification steps.
- Letting docs drift — update them in the same PR as behavior changes.

## References

- [onboarding-template.md](references/onboarding-template.md) — full README/onboarding packet template with section examples
- [output-format-templates.md](references/output-format-templates.md) — Notion and Confluence export formats
