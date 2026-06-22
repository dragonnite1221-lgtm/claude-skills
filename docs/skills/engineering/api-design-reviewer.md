---
title: "API Design Reviewer — Agent Skill for Codex & OpenClaw"
description: "Review REST API designs from OpenAPI/Swagger specs. api_linter.py checks resource naming, HTTP method usage, status codes, error-format consistency. Agent skill for Claude Code, Codex CLI, Gemini CLI, OpenClaw."
---

# API Design Reviewer

<div class="page-meta" markdown>
<span class="meta-badge">:material-rocket-launch: Engineering - POWERFUL</span>
<span class="meta-badge">:material-identifier: `api-design-reviewer`</span>
<span class="meta-badge">:material-github: <a href="https://github.com/alirezarezvani/claude-skills/tree/main/engineering/api-design-reviewer/SKILL.md">Source</a></span>
</div>

<div class="install-banner" markdown>
<span class="install-label">Install:</span> <code>claude /plugin install engineering-advanced-skills</code>
</div>


Analyze and review REST API designs for convention compliance, breaking changes, and overall
quality. Three stdlib-only tools operate on OpenAPI/Swagger JSON specs.

## Tools

| Tool | Purpose |
|------|---------|
| `scripts/api_linter.py` | Lint a spec for naming, HTTP methods, status codes, error formats, docs |
| `scripts/breaking_change_detector.py` | Diff two spec versions for breaking changes |
| `scripts/api_scorecard.py` | Grade design quality A–F across 5 weighted dimensions |

## Workflow

```bash
# 1. Lint a spec against REST conventions. Add --raw-endpoints for non-OpenAPI endpoint JSON.
python3 scripts/api_linter.py openapi.json
python3 scripts/api_linter.py --format json openapi.json --output report.json

# 2. Detect breaking changes between versions. --exit-on-breaking fails CI (exit 1).
python3 scripts/breaking_change_detector.py v1.json v2.json --exit-on-breaking

# 3. Score the design. --min-grade fails CI if below threshold.
python3 scripts/api_scorecard.py openapi.json --min-grade B
```

Fix the issues each tool reports, then re-run that step until it passes. All three accept
`--format text|json` and `--output`. The scorecard weights **consistency 30%**, documentation
20%, security 20%, usability 15%, performance 15%.

## CI Gate

The linter, detector, and scorecard share exit codes, so a local green run matches CI:

```bash
python3 scripts/api_linter.py api/openapi.json \
  && python3 scripts/breaking_change_detector.py api/v1.json api/openapi.json --exit-on-breaking \
  && python3 scripts/api_scorecard.py api/openapi.json --min-grade B
```

## What Good Looks Like

- **Resources, not actions** — `/api/v1/user-profiles` (kebab-case), not `/getUsers`.
- **Correct HTTP semantics** — GET (safe/idempotent), POST (create), PUT (replace/idempotent),
  PATCH (partial), DELETE (idempotent); pair each with the right status code (400/401/403/404/
  409/422/429/500).
- **Consistent error envelope** — `error.code`, `error.message`, `error.details[]`, `requestId`,
  `timestamp`.
- **Paginated lists** — offset, cursor, or page-based, returned in a `pagination` block.
- **Versioning** — URL versioning (`/api/v1/…`) is the default recommendation.

**Breaking** (needs a version bump): removing fields/endpoints, making optional fields required,
changing field types, changing URL structure, altering the error format. **Non-breaking:** adding
optional request fields, adding response fields, adding endpoints, relaxing required→optional.

Full rules, examples, and anti-patterns:

| File | Contents |
|------|----------|
| [rest_design_rules.md](https://github.com/alirezarezvani/claude-skills/tree/main/engineering/api-design-reviewer/references/rest_design_rules.md) | Naming, methods, versioning, pagination, errors, auth, rate limiting, caching, idempotency, HATEOAS |
| [api_antipatterns.md](https://github.com/alirezarezvani/claude-skills/tree/main/engineering/api-design-reviewer/references/api_antipatterns.md) | Common anti-patterns (verb URLs, over-nesting, inconsistent formats, missing pagination/rate limits) and fixes |
