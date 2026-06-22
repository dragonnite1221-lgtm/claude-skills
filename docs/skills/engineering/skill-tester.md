---
title: "Skill Tester — Agent Skill for Codex & OpenClaw"
description: "Validate and quality-score Claude skill packages before publishing. Checks SKILL.md frontmatter (name + description) and structure, runs each Python. Agent skill for Claude Code, Codex CLI, Gemini CLI, OpenClaw."
---

# Skill Tester

<div class="page-meta" markdown>
<span class="meta-badge">:material-rocket-launch: Engineering - POWERFUL</span>
<span class="meta-badge">:material-identifier: `skill-tester`</span>
<span class="meta-badge">:material-github: <a href="https://github.com/alirezarezvani/claude-skills/tree/main/engineering/skill-tester/SKILL.md">Source</a></span>
</div>

<div class="install-banner" markdown>
<span class="install-label">Install:</span> <code>claude /plugin install engineering-advanced-skills</code>
</div>


Validates and scores skill packages against this repository's skill contract:
`name` + `description` frontmatter, a documented body with a title, and
optional `scripts/` (stdlib-only Python CLIs), `references/`, and `assets/`.

## Tools

| Tool | Purpose |
|------|---------|
| `scripts/skill_validator.py` | Structure, frontmatter, and title/section compliance |
| `scripts/script_tester.py` | Runs each Python tool: syntax, argparse, `--help`, sample exec |
| `scripts/quality_scorer.py` | 0-100 documentation/structure score (optional security pass) |

`security_scorer.py` is a library used by `quality_scorer.py --include-security`.

## Validation workflow

Run the gates in order. On any failure, fix the reported issues and re-run that
step before moving on — only publish once all gates pass:

```bash
# 1. Structure + frontmatter. Exits non-zero on contract errors.
python3 scripts/skill_validator.py path/to/skill --json

# 2. If step 1 fails, fix the listed issues, then re-run step 1.

# 3. Script behaviour: syntax, argparse, --help, sample run.
python3 scripts/script_tester.py path/to/skill --json

# 4. Quality score — gate publishing at >= 70.
python3 scripts/quality_scorer.py path/to/skill --include-security --minimum-score 70
```

Enforce a tier's stricter directory/script requirements with `--tier`:

```bash
python3 scripts/skill_validator.py path/to/skill --tier POWERFUL --json
```

## What it checks

- **Contract** — `name` + `description` frontmatter (matching the repo's
  enforced gate, `scripts/validate-skill-frontmatter.py`), a top-level title,
  and minimum substance. Body section names are not mandated.
- **Scripts** — standard-library-only imports, `argparse`, an
  `if __name__ == "__main__"` guard (either quote style), `--help`, and a
  successful run on sample data.
- **Quality** — documentation completeness and structure, scored 0-100.

Detailed criteria live in references (kept out of this file to stay lean):

- [Tier requirements matrix](https://github.com/alirezarezvani/claude-skills/tree/main/engineering/skill-tester/references/tier-requirements-matrix.md) — BASIC / STANDARD / POWERFUL
- [Quality scoring rubric](https://github.com/alirezarezvani/claude-skills/tree/main/engineering/skill-tester/references/quality-scoring-rubric.md)
- [Skill structure specification](https://github.com/alirezarezvani/claude-skills/tree/main/engineering/skill-tester/references/skill-structure-specification.md)

## CI usage

Humans and CI run the same commands, so a local green run matches CI. Gate a PR
on the validator exit code plus a quality threshold:

```bash
python3 scripts/skill_validator.py "$skill" \
  && python3 scripts/quality_scorer.py "$skill" --minimum-score 70
```

Add `--json` to any tool for machine-readable output to feed dashboards or
PR comments.
