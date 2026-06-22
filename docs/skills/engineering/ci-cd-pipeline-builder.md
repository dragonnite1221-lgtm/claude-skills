---
title: "CI/CD Pipeline Builder — Agent Skill for Codex & OpenClaw"
description: "Detect a repository's stack from lockfiles and manifests (npm/yarn/pnpm via package-lock/yarn.lock/pnpm-lock, Python via. Agent skill for Claude Code, Codex CLI, Gemini CLI, OpenClaw."
---

# CI/CD Pipeline Builder

<div class="page-meta" markdown>
<span class="meta-badge">:material-rocket-launch: Engineering - POWERFUL</span>
<span class="meta-badge">:material-identifier: `ci-cd-pipeline-builder`</span>
<span class="meta-badge">:material-github: <a href="https://github.com/alirezarezvani/claude-skills/tree/main/engineering/ci-cd-pipeline-builder/SKILL.md">Source</a></span>
</div>

<div class="install-banner" markdown>
<span class="install-label">Install:</span> <code>claude /plugin install engineering-advanced-skills</code>
</div>


Generates pragmatic CI/CD pipelines from detected stack signals instead of guesswork.
Two stdlib-only CLI tools: a stack detector emits a JSON report that the pipeline
generator turns into committable GitHub Actions or GitLab CI YAML.

## Tools

| Tool | Purpose |
|------|---------|
| `scripts/stack_detector.py` | Detect package manager, runtime, and lint/test/build commands from repo files |
| `scripts/pipeline_generator.py` | Generate GitHub Actions or GitLab CI YAML from the detection report |

Both accept `--input report.json`, stdin JSON, or `--repo .` for auto-detection,
and emit `--format text` (human summary) or `--format json` (automation).

## Workflow

Detect the stack first, then generate the pipeline from that report. On a mismatch,
fix the report (or the underlying repo signals) and regenerate.

```bash
# 1. Detect stack. Writes a JSON report listing package managers + commands.
python3 scripts/stack_detector.py --repo . --format text
python3 scripts/stack_detector.py --repo . --format json > detected-stack.json

# 2. Generate a pipeline from the report (--platform is required).
python3 scripts/pipeline_generator.py \
  --input detected-stack.json \
  --platform github \
  --output .github/workflows/ci.yml \
  --format text

# End-to-end from the repo (auto-detects, no intermediate file):
python3 scripts/pipeline_generator.py --repo . --platform gitlab --output .gitlab-ci.yml
```

`--platform` accepts `github` or `gitlab`. Without `--output`, YAML prints to stdout.

## What each tool reports

**`stack_detector.py`** — checks for `package-lock.json`/`yarn.lock`/`pnpm-lock.yaml`,
`requirements.txt`/`pyproject.toml`, and `go.mod`; resolves the package manager
(npm/yarn/pnpm) and runtime (Node/Python/Go); and derives lint/test/build commands
from `package.json` scripts when present, falling back to conservative defaults
(`ruff check` + `pytest` for Python, `go vet`/`go test`/`go build` for Go).

**`pipeline_generator.py`** — emits a minimal, reliable pipeline: checkout → runtime
setup → cached dependency install → separate lint/test/build steps. Caching is keyed
to the detected package manager. Layer matrix builds, security scans, and deploy
gates on top of this baseline.

## Validate before merge

1. Confirm the referenced `lint`/`test`/`build` commands actually exist in the repo.
2. Check the generated YAML parses and runs locally where possible.
3. Document required secrets/env vars; never hardcode them in YAML.
4. Keep deploy jobs gated behind protected branches/environments with manual approval.

## Deployment gates

Start CI-only (lint/test/build), then add a staging deploy with explicit environment
context, then a production deploy behind a manual approval gate on a protected branch.
Keep rollout/rollback commands explicit. Gate policy and the
`develop`→staging / `main`→production pattern are in
[deployment-gates.md](https://github.com/alirezarezvani/claude-skills/tree/main/engineering/ci-cd-pipeline-builder/references/deployment-gates.md).

## Common pitfalls

- Copying a Node pipeline into a Python/Go repo (detect the stack first).
- Enabling deploy jobs before tests are stable.
- Forgetting dependency cache keys, or mismatching them to the package manager.
- Hardcoding secrets in YAML instead of using CI secret stores.
- Missing branch protections around production deploy jobs.

## References

- [github-actions-templates.md](https://github.com/alirezarezvani/claude-skills/tree/main/engineering/ci-cd-pipeline-builder/references/github-actions-templates.md) — Node/Python baseline workflows
- [gitlab-ci-templates.md](https://github.com/alirezarezvani/claude-skills/tree/main/engineering/ci-cd-pipeline-builder/references/gitlab-ci-templates.md) — Node/Python baseline stages
- [deployment-gates.md](https://github.com/alirezarezvani/claude-skills/tree/main/engineering/ci-cd-pipeline-builder/references/deployment-gates.md) — gate policy, environment pattern, rollback
- [README.md](https://github.com/alirezarezvani/claude-skills/tree/main/engineering/ci-cd-pipeline-builder/README.md) — quick start and installation
