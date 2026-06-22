---
title: "Runbook Generator — Agent Skill for Codex & OpenClaw"
description: "Scaffold a markdown operational runbook for a service from its name using runbook_generator.py — emits standard sections (Overview, Preconditions. Agent skill for Claude Code, Codex CLI, Gemini CLI, OpenClaw."
---

# Runbook Generator

<div class="page-meta" markdown>
<span class="meta-badge">:material-rocket-launch: Engineering - POWERFUL</span>
<span class="meta-badge">:material-identifier: `runbook-generator`</span>
<span class="meta-badge">:material-github: <a href="https://github.com/alirezarezvani/claude-skills/tree/main/engineering/runbook-generator/SKILL.md">Source</a></span>
</div>

<div class="install-banner" markdown>
<span class="install-label">Install:</span> <code>claude /plugin install engineering-advanced-skills</code>
</div>


Generate a markdown runbook skeleton for a service, then fill in the
service-specific commands, URLs, and escalation contacts. One stdlib-only CLI
emits a consistent section layout so every service's ops docs look the same.

## Tool

`scripts/runbook_generator.py SERVICE` writes a runbook to stdout (or a file)
with these sections: Overview, Preconditions, Start Procedure, Stop Procedure,
Health Checks, Deployment Checklist, Rollback, Incident Response, Escalation,
and Post-Incident. Each procedure section ships an example command block to
replace.

```bash
# Print to stdout
python3 scripts/runbook_generator.py payments-api

# Label owner + environment and write to the repo near the service
python3 scripts/runbook_generator.py payments-api \
  --owner platform --environment production \
  --output docs/runbooks/payments-api.md
```

Flags: `--owner` (ownership/escalation label), `--environment` (primary env),
`--output` (path; prints to stdout if omitted).

## Workflow

1. Generate the skeleton with `runbook_generator.py`.
2. Replace every example command with the real, copy-pasteable command.
3. Add an expected-output / health check after each critical step and define
   explicit rollback triggers.
4. Dry-run the procedures in staging — if a step fails or output doesn't match,
   fix the runbook text and re-run until it executes cleanly.
5. Commit the runbook in version control next to the service code.

## Common Pitfalls

- Missing rollback triggers or rollback commands.
- Steps without an expected-output check.
- Stale ownership/escalation contacts.
- Runbooks never tested outside of a live incident.

Keep commands copy-pasteable, verify a health check after every critical step,
and update content after each incident/postmortem. Section patterns and filled
examples: [references/runbook-templates.md](https://github.com/alirezarezvani/claude-skills/tree/main/engineering/runbook-generator/references/runbook-templates.md).
