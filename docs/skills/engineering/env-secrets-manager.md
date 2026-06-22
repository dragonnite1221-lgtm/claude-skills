---
title: "Env & Secrets Manager — Agent Skill for Codex & OpenClaw"
description: "Audit a repository working tree for hardcoded secret leaks (AWS keys, Stripe/Slack/GitHub tokens, JWTs, private keys, credentialed connection. Agent skill for Claude Code, Codex CLI, Gemini CLI, OpenClaw."
---

# Env & Secrets Manager

<div class="page-meta" markdown>
<span class="meta-badge">:material-rocket-launch: Engineering - POWERFUL</span>
<span class="meta-badge">:material-identifier: `env-secrets-manager`</span>
<span class="meta-badge">:material-github: <a href="https://github.com/alirezarezvani/claude-skills/tree/main/engineering/env-secrets-manager/SKILL.md">Source</a></span>
</div>

<div class="install-banner" markdown>
<span class="install-label">Install:</span> <code>claude /plugin install engineering-advanced-skills</code>
</div>


Audits environment-variable hygiene and detects hardcoded secrets across local
development and CI workflows.

## Tool

`scripts/env_auditor.py` scans a repository's working tree (env files and source)
for likely secret leaks and returns severity-ranked findings.

```bash
python3 scripts/env_auditor.py /path/to/repo               # human-readable
python3 scripts/env_auditor.py /path/to/repo --json        # JSON for CI gates
python3 scripts/env_auditor.py /path/to/repo --max-file-size-kb 256  # skip large files
```

## Audit workflow

1. Run `env_auditor.py` on the repository root.
2. Triage `critical` and `high` findings first; confirm each is a real credential.
3. Rotate every confirmed-real credential (see rotation below) and remove the value.
4. Update `.env.example` (placeholders only) and `.gitignore` so `.env*` stays local.
5. Add or tighten a pre-commit / CI secret-scanning gate, then re-run the audit to
   confirm a clean tree.

Detected categories and severity rationale are in
[secret-patterns.md](https://github.com/alirezarezvani/claude-skills/tree/main/engineering/env-secrets-manager/references/secret-patterns.md). Ready-to-use validation,
working-tree/history scan, and pre-commit hook scripts are in
[validation-detection-rotation.md](https://github.com/alirezarezvani/claude-skills/tree/main/engineering/env-secrets-manager/references/validation-detection-rotation.md).

## Credential rotation

When a secret is confirmed leaked, bound its useful lifetime by rotating:

1. **Revoke** the compromised credential at the provider immediately.
2. **Generate** a replacement and **deploy** it to all consumers (apps, services,
   pipelines) in parallel.
3. **Verify** each consumer authenticates with the new credential before revoking.
4. **Audit** access logs for unauthorized use during the exposure window.
5. **Scrub** the value from git history, CI logs, and artifact registries.
6. **Record** the rotation timestamp and file an incident report.

Step-by-step rotation, git-history scrubbing, and per-provider update commands
(Vault KV v2, AWS SSM, 1Password, Doppler) are in
[validation-detection-rotation.md](https://github.com/alirezarezvani/claude-skills/tree/main/engineering/env-secrets-manager/references/validation-detection-rotation.md).
Automate rotation where supported: AWS Secrets Manager Lambda rotation, Vault
dynamic secrets with TTLs, Azure Event Grid triggers, GCP Pub/Sub + Cloud Functions.

## Production secret stores

Production apps should read secrets from a dedicated store, never from `.env` files
or image-baked environment variables.

- **Single cloud** — use the cloud-native manager (AWS Secrets Manager, Azure Key
  Vault, GCP Secret Manager); tight IAM integration, lower overhead.
- **Multi-cloud / hybrid** — HashiCorp Vault for a uniform API and dynamic,
  auto-expiring secrets.
- **Kubernetes** — External Secrets Operator or the Secrets Store CSI Driver syncs
  any backend into the cluster without hardcoding.

Access patterns: SDK/API pull at startup, sidecar injection (Vault Agent), init
container, or CSI volume mount. For production vault infrastructure (HA, DR), see the
`engineering/secrets-vault-manager` skill.

## CI/CD secret injection

- **GitHub Actions** — `${{ secrets.NAME }}` repo/environment secrets; prefer OIDC
  federation (`role-to-assume`) over long-lived keys; environment secrets add
  reviewer gates. Never `echo`/`toJSON()` a secret.
- **GitLab CI** — `masked` + `protected` CI/CD variables scoped per environment, or
  the Vault integration (`secrets:vault`) for dynamic injection.
- **Universal** — short-lived tokens (OIDC/STS) over static creds; never print secret
  values; don't expose secrets to fork-triggered pipelines; rotate CI secrets on the
  same schedule as app secrets; periodically audit pipeline logs.

## Audit logging

Track who read which secret and when: AWS CloudTrail (`GetSecretValue`), Azure
Activity/Diagnostic Logs, GCP Cloud Audit Logs, or the Vault audit backend. Alert on
access from unknown IPs/service accounts, bulk reads, or access outside deployment
windows; feed logs into your SIEM and review during access recertification.

## Common pitfalls

- Real values committed in `.env.example`.
- Rotating one system but missing downstream consumers.
- Logging secrets during debugging or incident response.
- Treating a suspected leak as low urgency without validating it.
